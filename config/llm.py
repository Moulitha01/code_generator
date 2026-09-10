from langchain_groq import ChatGroq

from config.groq_key_manager import groq_key_manager


MODEL_NAME = "openai/gpt-oss-120b"


def get_llm(temperature=0.4):

    return ChatGroq(
        model=MODEL_NAME,
        temperature=temperature,
        api_key=groq_key_manager.get_key()
    )


def invoke_with_failover(prompt, temperature=0.4):

    total_keys = len(groq_key_manager.keys)

    for attempt in range(total_keys):

        try:
            llm = get_llm(temperature)

            print(
                f"Using Groq API key "
                f"{groq_key_manager.current_index + 1}"
            )

            response = llm.invoke(prompt)

            return response

        except Exception as e:

            error = str(e).lower()

            if (
                "429" in error
                or "rate limit" in error
                or "too many requests" in error
            ):

                print(
                    f"Key {groq_key_manager.current_index + 1} "
                    "rate limited. Switching key..."
                )

                groq_key_manager.next_key()

            elif (
                "401" in error
                or "invalid api key" in error
                or "authentication" in error
            ):

                print(
                    f"Key {groq_key_manager.current_index + 1} "
                    "is invalid. Switching key..."
                )

                groq_key_manager.next_key()

            else:
                raise

    raise RuntimeError(
        "All Groq API keys failed or reached their limits."
    )