
import streamlit as st

from agents.orchestrator import OrchestratorAgent


st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)


st.title("🔎 Multi-Agent Research Assistant")

st.write(
    "Research a topic using web search, source extraction, "
    "fact checking, analysis, and AI synthesis."
)


question = st.text_area(
    "What would you like to research?",
    placeholder="Example: How is AI being used in semiconductor manufacturing?",
    height=120,
)


if st.button("🚀 Start Research", type="primary"):
    if not question.strip():
        st.warning("Please enter a research question.")

    else:
        with st.spinner("Researching..."):
            orchestrator = OrchestratorAgent()

            result = orchestrator.run(
                question.strip(),
                max_results=3,
            )

        st.success("Research completed!")

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📄 Final Report",
                "✅ Fact Check",
                "📊 Analysis",
                "🔗 Sources",
            ]
        )

        with tab1:
            st.markdown(result["final_report"])

        with tab2:
            st.markdown(result["fact_check"])

        with tab3:
            st.markdown(result["analysis"])

        with tab4:
            for index, source in enumerate(result["sources"], start=1):
                st.subheader(f"Source {index}")

                st.write(
                    source.get("title", "Untitled source")
                )

                st.write(
                    source.get("url", "")
                )

                if source.get("success"):
                    st.success("Content extracted successfully.")
                else:
                    st.warning(
                        "Could not extract content from this source."
                    )

# Footer
st.markdown(
    "<div style='text-align: center; margin-top: 40px; padding: 20px; "
    "border-top: 1px solid rgba(128,128,128,0.2);'>"
    "<p style='font-size: 15px; color: #888;'>"
    "<strong>Created & Developed by Annapoorna S U</strong>"
    "</p>"
    "<p style='font-size: 13px; color: #888;'>"
    "Multi-Agent Research Assistant"
    "</p></div>",
    unsafe_allow_html=True,
)