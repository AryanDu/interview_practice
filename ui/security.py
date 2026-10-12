"""Security Testing tab - Jailbreak tests with a persistent results view and working Excel export."""
from io import BytesIO
import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def render_security_testing_tab():
    """Run the security suite and keep results visible across Streamlit reruns."""
    st.markdown(
        '<section class="v2-workspace-intro"><div class="v2-page-kicker">GUARDRAILS & TRUST</div>'
        '<h1>Security Testing</h1><p>Run the existing jailbreak test suite, inspect results and export the output for review.</p></section>',
        unsafe_allow_html=True,
    )
    st.warning("This runs security tests against the application's existing guardrails; it does not change authentication or access settings.")

    if st.button("🚀 Run Jailbreak Tests", type="primary"):
        try:
            from tests.jailbreak_tests import JailbreakTester

            with st.spinner("Running security tests..."):
                tester = JailbreakTester()
                st.session_state.security_test_results = tester.run_all_tests()
            st.success("✅ Tests completed!")
        except Exception:
            logger.exception("Security test suite failed")
            st.error("The security suite could not run. Please check the deployment logs.")
            return

    results_df = st.session_state.get("security_test_results")
    if results_df is None:
        with st.container(border=True):
            st.markdown("### No test run yet.")
            st.write("Run the suite when you're ready. Results will stay visible during this session and can be exported to Excel.")
        return

    st.dataframe(results_df, use_container_width=True)
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            results_df.to_excel(writer, index=False, sheet_name="Security Results")
        st.download_button(
            "📥 Export Results to Excel",
            data=output.getvalue(),
            file_name="security_test_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except Exception:
        logger.exception("Security result Excel export failed")
        st.error("The Excel export could not be created. Please try again.")
