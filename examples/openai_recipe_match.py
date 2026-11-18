"""Run after installing the project: python examples/openai_recipe_match.py."""

from moji_demo.providers import run_openai


if __name__ == "__main__":
    print(run_openai("I want to cook dal. Which Moji Masala recipe and spices should I use?"))
