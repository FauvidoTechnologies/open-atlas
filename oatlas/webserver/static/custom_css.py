main_css = """ <style>
        /* Matte dark background */
        .stApp {
            background-color: #121212;
            color: white;
        }
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;
            padding-top: 2rem;
        }
        /* Navigation buttons */
        .nav-button {
            display: block;
            padding: 10px 16px;
            margin: 5px 0;
            color: white;
            background-color: transparent;
            border: none;
            text-align: left;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            border-radius: 6px;
        }
        .nav-button:hover {
            background-color: #333333;
        }
        .nav-button.active {
            background-color: #444444;
        }
        /* Center header */
        .center-header {
            text-align: center;
        }
    </style>"""
