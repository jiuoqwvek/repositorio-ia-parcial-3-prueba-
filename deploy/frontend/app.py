from streamlit import hello

if __name__ == '__main__':
    # Placeholder entrypoint used by the course deploy layout.
    # The real frontend lives at ../frontend/app.py but deploy/ contains a copy.
    import streamlit.web.bootstrap as stb
    stb.run()
