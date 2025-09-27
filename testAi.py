from meta_ai_api import MetaAI

ai = MetaAI()

def ai_function():
    """Generate a short BlockScroll-style motivational notification about scrolling."""
    prompt = (
        "Write a single short push-notification text mocking endless scrolling. "
        "Style: achievement unlocked / streak / gaming reward tone. "
        "It should highlight wasted hours scrolling with a clever, realistic twist "
        "about regret, lost time, or missed success. But motivating and realistic do not say you could have writtern a novel and all"
        "Examples: 'Elon Musk made millions while you scrolled 2h — unlocked: regret!'. "
        "Keep it under 100 characters. "
        "Do not explain, list, or say 'here are options'. "
        "Output only one notification text, nothing else."
    )
    response_dict = ai.prompt(message=prompt)

    # Extract the message safely
    response = response_dict.get("message", "").strip()

    # Remove filler like "Here are some options:" if it appears
    if response.lower().startswith("here are"):
        response = response.split(":", 1)[-1].strip()

    # If multiple lines or options come back, take just the first
    if "\n" in response:
        response = response.split("\n")[0].strip()

    print(response)
    return response


ai_function()
