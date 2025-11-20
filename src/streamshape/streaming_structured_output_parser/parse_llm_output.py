import json
import random
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type

from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI

class _StreamClient:
    """Wrap streaming response handling with cancellation support."""

    def __init__(self, response: Any, cancel_event: Any,request_type:str, *, encoding: str = "utf-8") -> None:
        self._response = response
        self._cancel_event = cancel_event
        self._encoding = encoding
        self.type = request_type

    def iter_lines(self) -> Iterator[str]:
        try:
            if self.type == "http":
                yield from self._iter_http_stream()
            else:
                yield from self._iter_openai_stream()
        finally:
            try:
                self._response.close()
            except Exception:
                pass

    def _iteration_cancelled(self) -> bool:
        if self._cancel_event and self._cancel_event.is_set():
            print("\n❌ Stream cancelled")
            try:
                self._response.close()
            except Exception:
                pass
            return True
        return False

    def _iter_http_stream(self) -> Iterator[str]:
        for raw in self._response.iter_lines():
            if self._iteration_cancelled():
                return

            if not raw:
                continue

            if isinstance(raw, (bytes, bytearray)):
                try:
                    yield raw.decode(self._encoding)
                except Exception:
                    yield raw.decode(self._encoding, errors="ignore")
            else:
                yield str(raw)

    def _iter_openai_stream(self) -> Iterator[str]:
        last_usage = None
        for raw in self._response:
            if self._iteration_cancelled():
                return

            chunk = raw.model_dump()

            if not chunk:
                continue

            # Capture usage if present in the chunk dict or raw object
            if "usage" in chunk and chunk["usage"]:
                last_usage = chunk["usage"]
            elif hasattr(raw, 'usage') and raw.usage:
                last_usage = raw.usage.model_dump() if hasattr(raw.usage, 'model_dump') else raw.usage

            yield f"data: {json.dumps(chunk)}"

            finish_reason = self._extract_finish_reason(chunk)
            if finish_reason is not None:
                # Mirror SSE terminator so downstream parser behaves consistently.
                yield "data: [DONE]"

    @staticmethod
    def _extract_finish_reason(chunk: Dict[str, Any]) -> Optional[str]:
        choices = chunk.get("choices") or []
        if not choices:
            return None

        first_choice = choices[0]
        return first_choice.get("finish_reason")


class _TokenBuffer:
    """Accumulate streamed content and emit complete JSON objects."""

    def __init__(self) -> None:
        self._buffer = ""
        self._array_started = False
        self._decoder = json.JSONDecoder()
        self._saw_chunk = False

    def feed(self, chunk: str) -> List[Any]:
        if not chunk:
            return []

        self._saw_chunk = True
        self._buffer += chunk
        parsed: List[Any] = []

        if not self._array_started:
            start_idx = self._buffer.find("[")
            if start_idx == -1:
                return []
            self._array_started = True
            self._buffer = self._buffer[start_idx + 1 :]

        while True:
            self._buffer = self._buffer.lstrip()
            if not self._buffer:
                break

            if self._buffer.startswith("]"):
                self._buffer = self._buffer[1:]
                self._array_started = False
                break

            try:
                obj, offset = self._decoder.raw_decode(self._buffer)
            except json.JSONDecodeError:
                break

            parsed.append(obj)
            self._buffer = self._buffer[offset:]
            self._buffer = self._buffer.lstrip()
            if self._buffer.startswith(","):
                self._buffer = self._buffer[1:]

        return parsed

    def saw_content(self) -> bool:
        return self._saw_chunk


class _SSEEventParser:
    """Decode SSE lines into JSON events and expose delta content."""

    _DATA_PREFIX = "data: "

    def parse_line(self, line: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        if not line.startswith(self._DATA_PREFIX):
            return None, False

        payload = line[len(self._DATA_PREFIX) :]
        if payload == "[DONE]":
            return None, True

        try:
            return json.loads(payload), False
        except json.JSONDecodeError:
            return None, False

    def content_from_event(self, event: Dict[str, Any]) -> Optional[str]:
        choices = event.get("choices")
        if not choices:
            return None

        first_choice = choices[0]
        delta = first_choice.get("delta")
        if not delta:
            return None

        content = delta.get("content")
        if not content:
            return None

        return content


class _SchemaValidator:
    """Validate parsed payloads against the provided Pydantic schema."""

    def __init__(self, schema: Type[BaseModel]) -> None:
        self._schema = schema

    def validate(self, payload: Any) -> Optional[BaseModel]:
        try:
            return self._schema.model_validate(payload)
        except ValidationError:
            return None


class _PipelineController:
    """Coordinate streaming, parsing, and validation."""

    def __init__(self, response: Any, cancel_event: Any, schema: Type[BaseModel],request_type:str) -> None:
        self._client = _StreamClient(response, cancel_event,request_type)
        self._parser = _SSEEventParser()
        self._buffer = _TokenBuffer()
        self._validator = _SchemaValidator(schema)
        self._usage_data = {}
        self._raw_chunks = []

    def stream(self) -> Iterator[Dict[str, Any]]:
        try:
            stream_finished = False
            final_yielded = False
            for line in self._client.iter_lines():
                event, finished = self._parser.parse_line(line)

                if finished:
                    stream_finished = True
                    if self._buffer.saw_content():
                        print("\n✅ Stream completed")
                    # Don't break yet, continue to get usage from next chunk
                    continue

                if not event:
                    continue

                # Store raw chunks for final result
                self._raw_chunks.append(event)

                # Extract usage data if present (comes after [DONE])
                if "usage" in event and event["usage"]:
                    self._usage_data = event["usage"]
                    # If stream already finished, yield final result now
                    if stream_finished:
                        yield {
                            "data": None,
                            "usage": self._usage_data,
                            "raw_chunks": self._raw_chunks,
                            "finished": True
                        }
                        final_yielded = True
                        break

                content = self._parser.content_from_event(event)
                if content:
                    for candidate in self._buffer.feed(content):
                        validated = self._validator.validate(candidate)
                        if validated is not None:
                            yield {
                                "data": validated,
                                "usage": {},
                                "finished": False
                            }
            
            # If loop ended without yielding final result, yield it now
            if not final_yielded:
                yield {
                    "data": None,
                    "usage": self._usage_data if self._usage_data else {},
                    "raw_chunks": self._raw_chunks,
                    "finished": True
                }
        except Exception as exc:
            print(f"Error processing line: {exc}")
            yield {
                "data": None,
                "usage": {},
                "raw_chunks": self._raw_chunks if hasattr(self, '_raw_chunks') else [],
                "finished": True,
                "error": f"error while generating -> {exc}"
            }


def read_tokens(response: Any,output_schema: Type[BaseModel],request_type:str,cancel_event: Any=None) -> Iterator[Dict[str, Any]]:
    controller = _PipelineController(response, cancel_event, output_schema,request_type)
    yield from controller.stream()