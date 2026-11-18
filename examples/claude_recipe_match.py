"""Run after installing the project: python examples/claude_recipe_match.py."""

from moji_demo.providers import run_claude


if __name__ == "__main__":
    print(run_claude("I want to cook dal. Which Moji Masala recipe and spices should I use?"))
