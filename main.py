from agents.researcher import ResearcherAgent


def main():
    print("=" * 60)
    print("MULTI-AGENT RESEARCH ASSISTANT")
    print("=" * 60)

    question = input("\nWhat would you like to research?\n> ").strip()

    if not question:
        print("Please enter a research question.")
        return

    researcher = ResearcherAgent()

    print("\nResearcher Agent is working...\n")

    result = researcher.research(question)

    print("=" * 60)
    print("RESEARCHER AGENT RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()