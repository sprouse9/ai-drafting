import json
import time
import urllib.error
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen2.5-coder:3b"
    #"llama3.2:3b",
    #"deepseek-coder:6.7b",
]


# This describes the exact JSON structure we require.
COMMAND_SCHEMA = {
    "type": "object",
    "properties": {
        "function": {
            "type": "string",
            "enum": ["draw_line"],
        },
        "arguments": {
            "type": "object",
            "properties": {
                "x1": {"type": "number"},
                "y1": {"type": "number"},
                "x2": {"type": "number"},
                "y2": {"type": "number"},
            },
            "required": ["x1", "y1", "x2", "y2"],
            "additionalProperties": False,
        },
    },
    "required": ["function", "arguments"],
    "additionalProperties": False,
}


TEST_CASES = [
    {
        "name": "horizontal_line",
        "request": (
            "Draw a horizontal line 100 mm long "
            "starting at the origin."
        ),
        "expected": {
            "function": "draw_line",
            "arguments": {
                "x1": 0,
                "y1": 0,
                "x2": 100,
                "y2": 0,
            },
        },
    },
    {
        "name": "vertical_line",
        "request": (
            "Draw a vertical line upward 75 mm long "
            "starting at (20, 10)."
        ),
        "expected": {
            "function": "draw_line",
            "arguments": {
                "x1": 20,
                "y1": 10,
                "x2": 20,
                "y2": 85,
            },
        },
    },
]


def ask_ollama(model: str, request_text: str) -> dict:
    prompt = f"""
You are a CAD command interpreter.

You have exactly one available function:

draw_line(x1, y1, x2, y2)

Parameter definitions:
- x1 and y1 are the absolute coordinates of the starting point.
- x2 and y2 are the absolute coordinates of the ending point.
- All coordinates are measured in millimeters.

Coordinate system:
- Positive x points right.
- Negative x points left.
- Positive y points up.
- Negative y points down.
- If a starting point and length are provided, calculate the ending coordinates.
- Do not use the line length directly as an ending coordinate.

Return only valid JSON using exactly this structure:

{{
  "function": "draw_line",
  "arguments": {{
    "x1": number,
    "y1": number,
    "x2": number,
    "y2": number
  }}
}}

Do not include markdown.
Do not include an explanation.
Do not add any other properties.

Request:
{request_text}
""".strip()


    print("\nPROMPT SENT TO MODEL:\n")
    print(prompt)
    print("\n" + "-" * 60)


    payload = {
        "model": model,
        "prompt": prompt,
        "format": COMMAND_SCHEMA,
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }

    encoded_payload = json.dumps(payload).encode("utf-8")

    http_request = urllib.request.Request(
        OLLAMA_URL,
        data=encoded_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(http_request, timeout=180) as response:
        ollama_result = json.loads(response.read().decode("utf-8"))

    # Ollama's response field contains the model-generated JSON text.
    return {
        "command": json.loads(ollama_result["response"]),
        "total_duration": ollama_result.get("total_duration", 0),
        "load_duration": ollama_result.get("load_duration", 0),
    }


def nanoseconds_to_seconds(value: int) -> float:
    return value / 1_000_000_000


def run_test(model: str, test_case: dict) -> bool:
    print(f"\nTesting: {model}")
    print(f"Test:    {test_case['name']}")

    start_time = time.perf_counter()

    try:
        result = ask_ollama(model, test_case["request"])
    except urllib.error.URLError as error:
        print(f"ERROR: Could not contact Ollama: {error}")
        return False
    except json.JSONDecodeError as error:
        print(f"FAIL: Model did not return valid JSON: {error}")
        return False
    except Exception as error:
        print(f"ERROR: {error}")
        return False

    elapsed_time = time.perf_counter() - start_time
    actual = result["command"]
    expected = test_case["expected"]
    passed = actual == expected

    print("Expected:")
    print(json.dumps(expected, indent=2))

    print("Actual:")
    print(json.dumps(actual, indent=2))

    print(f"Result:  {'PASS' if passed else 'FAIL'}")
    print(f"Elapsed: {elapsed_time:.2f} seconds")
    print(
        "Ollama total time: "
        f"{nanoseconds_to_seconds(result['total_duration']):.2f} seconds"
    )
    print(
        "Model load time:   "
        f"{nanoseconds_to_seconds(result['load_duration']):.2f} seconds"
    )

    return passed


def main() -> None:
    repeat_count = 1

    total_runs = 0
    passed_runs = 0

    for model in MODELS:
        print("\n" + "=" * 55)
        print(f"MODEL: {model}")
        print("=" * 55)

        for test_case in TEST_CASES:
            for run_number in range(1, repeat_count + 1):
                print(
                    f"\nRun {run_number}/{repeat_count} "
                    f"for {test_case['name']}"
                )

                total_runs += 1

                if run_test(model, test_case):
                    passed_runs += 1

    print("\n" + "=" * 55)
    print(f"Passed runs: {passed_runs}/{total_runs}")
    print("=" * 55)


if __name__ == "__main__":
    main()