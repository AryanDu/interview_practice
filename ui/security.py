"""
Security Testing tab - Jailbreak tests
"""
import streamlit as st


def render_security_testing_tab():
    """Security testing tab"""
    st.header("🔒 Security Testing (Jailbreak Tests)")
    st.warning("⚠️ This tab runs security tests to validate the application's security guards.")
    
    if st.button("🚀 Run Jailbreak Tests", type="primary"):
        from tests.jailbreak_tests import JailbreakTester
        
        with st.spinner("Running security tests..."):
            tester = JailbreakTester()
            results_df = tester.run_all_tests()
            
            st.success("✅ Tests completed!")
            st.dataframe(results_df, use_container_width=True)
            
            # Export results
            if st.button("📥 Export Results to Excel"):
                try:
                    filepath = tester.export_results(results_df)
                    st.success(f"✅ Results exported to: {filepath}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
