"""Security Testing tab - Jailbreak tests with a persistent results view and working Excel export."""
from io import BytesIO

import pandas as pd
import streamlit as st


def render_security_testing_tab():
    """Run the security suite and keep results visible across Streamlit reruns."""
    st.header("🔒 Security Testing (Jailbreak Tests)")
    st.warning("⚠️ This tab runs security tests to validate the application's security guards.")

    if st.button("🚀 Run Jailbreak Tests", type="primary"):
        try:
            from tests.jailbreak_tests import JailbreakTester

            with st.spinner("Running security tests..."):
                tester = JailbreakTester()
                st.session_state.security_test_results = tester.run_all_tests()
            st.success("✅ Tests completed!")
        except Exception as exc:
            st.error(f"Could not run the security suite: {exc}")
            return

    results_df = st.session_state.get("security_test_results")
    if results_df is None:
        st.info("Run the test suite to view results and enable the Excel export.")
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
    except Exception as exc:
        st.error(f"Excel export failed: {exc}")
