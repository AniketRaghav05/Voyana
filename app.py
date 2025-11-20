import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_option_menu import option_menu
import json
from PIL import Image
from streamlit_lottie import st_lottie
from openai import OpenAI

st.set_page_config(page_title="Global Travel & Holidays", layout="wide")

#  GLOBAL CSS
st.markdown(
    """
    <style>
    @media (min-width: calc(736px + 8rem)) {
        .st-emotion-cache-zy6yx3 {
        padding-left: 5rem;
        padding-right: 5rem;
        }
    }
    .st-emotion-cache-zy6yx3 {
    width: 90%;
    padding: 2rem 0rem 9rem 0rem;
    max-width: initial;
    min-width: auto;
    }
    .stApp { background-color: #E6F2FF; }
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    header[data-testid="stHeader"] div {
        box-shadow: none !important;
    }
    body, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #000000; text-align: center;
    }
    ul, ol, li {
        text-align: center !important; 
        list-style-position: inside;
    }
    .stButton > button {
        background-color: #FF8C42; 
        color: white; 
        border-radius: 10px;
    }
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #FF8C42; color: #FFFFFF;
    }
    .news-card, .blog-post-card {
        border: 1px solid #ccc; 
        border-radius: 8px; 
        padding: 15px; 
        margin-bottom: 15px;
        background-color: #ffffff; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: left !important;
    }
    .news-card a {text-decoration: none; color: #FF8C42;}
    .blog-post-card h4 {color: #FF8C42; margin-top: 0;}
    div[data-testid="stColumn"] div[data-testid="stTabs"] {
        border: 1px solid #FF8C42; border-radius: 8px; padding: 10px; background-color: #f0f2f6;
    }
    div[data-testid="stColumn"] div[data-testid="stTabContent"] {
        border-top: 1px solid #FF8C42; padding-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# FIREBASE SETUP#
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")

db = firestore.client()

#  OPENAI SETUP
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# SESSION STATE  
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "selected" not in st.session_state:
    st.session_state.selected = "Home" if st.session_state.logged_in else "Login/Signup"
if "latest" not in st.session_state:
    st.session_state["latest"] = ("", "")
if "show_ai" not in st.session_state:
    st.session_state["show_ai"] = False

# FUNCTIONS 
def store_blog_post(author, title, content):
    blogs_ref = db.collection('blogs')
    blogs_ref.add({
        'author': author,
        'title': title,
        'content': content,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    st.success("Blog post submitted successfully!")

def get_blogs():
    blogs_ref = db.collection('blogs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(2)
    docs = blogs_ref.stream()
    return [doc.to_dict() for doc in docs]

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# NAVIGATION BAR 
if st.session_state.logged_in:
    left_col, center_col, right_col = st.columns([1, 4, 1])
    # ---- LEFT: App Name ----
    with left_col:
        st.markdown(
            """
            <div style="font-size:24px; font-weight:bold; color:#FF8C42; padding:0px;">
                VOYANA
            </div>
            """, unsafe_allow_html=True
        )

    # ---- CENTER: Navigation Buttons ----
    with center_col:
        # Include "Home" as the first page
        pages = ["Home", "Dashboard", "Case-Study", "Blogs/News", "Feedback", "Settings", "Support"]

        nav_cols = st.columns(len(pages))
        for i, page in enumerate(pages):
            # Highlight the selected page
            if st.session_state.selected == page:
                btn_color = "#E6F2FF"
            else:
                btn_color = "#E6F2FF"

            if nav_cols[i].button(page, key=f"nav_{page}"):
                st.session_state.selected = page
                st.rerun()

            # Add inline CSS to color buttons
            nav_cols[i].markdown(
                f"""
                <style>
                div.stButton > button[kind] {{
                    background-color: {btn_color} !important;
                    color: white;
                    border-radius: 5px;
                    font-size: 8px !important;      
                    padding: 3px 6px;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            

    with right_col:
        user = st.session_state.current_user
        col_spacer, col2, col3,  = st.columns([1.8, 1, 1],gap="small")  # small width for buttons, spacer pushes them right

        with col_spacer: 
            st.empty()

        with col3:
            if st.button("👤", key="profile_button"):
                st.session_state.selected = "Profile"

        with col2:
            if st.button("AI"):
                st.session_state["show_ai"] = True

else:
    selected = "Login/Signup"


if st.session_state.selected == "Home":
    st.markdown(
    """
    <div style="
        text-align:center; 
        padding: 25px; 
        background-color: #B3D9FF;
        border-radius: 12px; 
        margin-bottom:20px;
        color:black;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);  /* Soft shadow for depth */
        border: 2px solid #FF8C42; 
    ">
        <h3 style="color:orange; font-weight:bold;">WELCOME TO VOYANA</h3>
        <h1 style="margin-bottom:10px;">Discover Global Travel & Holidays Through Interactive Data</h1>
        <h3>Discover. Explore. Experience.</h3>
        <p style="font-size:16px;">
            VOYANA is your window to the world of travel, transforming complex global holiday and tourism data
            into beautiful, insightful, and interactive visualizations. Uncover trends, explore destinations, 
            and understand the stories behind the numbers.
        </p>
    </div>
    """,
    unsafe_allow_html=True  
    )

    st.markdown("### Quick Travel Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Top Destinations", "Paris, Greenland, Dubai")
    with col2:
        lottie_anim = load_lottiefile("globe.json")  # your file name
        st.markdown(
        """
        <div style="background-color:#E6F2FF; border-radius:12px; padding:10px; display:inline-block;">
        """,
        unsafe_allow_html=True
        )

        st_lottie(
            lottie_anim,
            speed=1,
            loop=True,
            quality="high",
            height=200,
            key="globe_anim"
        )
    st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.metric("Avg. Spend per Trip", "$2,450")
    st.markdown("---")

    st.markdown("### Featured Destinations")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://i1.wp.com/beautifulplacestovisit.com/wp-content/uploads/2011/05/Tour_eiffel_paris-eiffel_tower.jpg", caption="Paris, France")
    with col2:
        st.image("https://media.istockphoto.com/id/863187200/photo/greenlanic-northern-lights.webp?b=1&s=170667a&w=0&k=20&c=EkF0XoSZvx2Mi79UeMF_-62ClwG6tuerCc2UtyWCSGw=", caption="Greenland")
    with col3:
        st.image("https://d1gu3pii8scrhd.cloudfront.net/s3fs-public/editorial/bigstock-burj-dubai-8847490.jpg", caption="Dubai, UAE")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
        """
        <div style="height:400px; display:flex; flex-direction:column; justify-content:center;">
            <h3>About Voyana</h3>
            <p>
                Our platform is designed to uncover key trends, patterns, and insights from a rich tourism dataset, making complex information both accessible and engaging.
            </p>
            <p>
                Through our interactive dashboard, you can dive into popular destinations, track demographic shifts in tourism, and analyze global holiday spending with ease. 
            </p>
            <p>
                    At Voyana, we believe travel data tells a bigger story—about culture, economies, and human behavior—and our mission is to bring these insights to life in a way that inspires curiosity and discovery.
            </p>
        </div>
        """,
        unsafe_allow_html=True
        )

    with col2:
        st.markdown(
        """
        <div style="height:400px; display:flex; justify-content:center; align-items:center;">
            <img src="https://st2.depositphotos.com/1128150/6491/i/950/depositphotos_64914571-stock-photo-collage-of-summer-sardinia-images.jpg"
                 style="height:100%; width:100%; object-fit:cover; border-radius:10px;">
        </div>
        """,
        unsafe_allow_html=True
    )


elif st.session_state.selected == "Login/Signup":
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; padding: 25px; background: linear-gradient(90deg, #FF8C42, #FFB347); border-radius: 12px; margin-bottom:20px;">
                <h1 style="color:white; margin-bottom:10px;">Welcome to Voyana</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.title("Login / Signup")
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user_ref = db.collection("users").document(login_username).get()
                if user_ref.exists:
                    user_data = user_ref.to_dict()
                    if user_data["password"] == login_password:
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_username
                        st.session_state.selected = "Home"
                        st.success(f"Welcome back, {login_username}!")
                        st.rerun()
                    else:
                        st.error("Incorrect password")
                else:
                    st.error("Username not found")

        with tab2:
            new_username = st.text_input("Choose a Username", key="signup_username")
            new_email = st.text_input("Enter Email", key="signup_email")
            new_password = st.text_input("Create Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                user_ref = db.collection("users").document(new_username).get()
                if user_ref.exists:
                    st.error("Username already exists!")
                elif new_username == "" or new_password == "" or new_email == "":
                    st.error("⚠ Please fill all fields")
                else:
                    db.collection("users").document(new_username).set({
                        "email": new_email,
                        "password": new_password
                    })
                    st.session_state.logged_in = True
                    st.session_state.current_user = new_username
                    st.session_state.selected = "Home"  
                    st.success(" Account created successfully! Please log in.")
                    st.rerun()

elif st.session_state.selected == "Profile":
    if not st.session_state.logged_in:
        st.warning("⚠ You are not logged in. Please go to **Login/Signup**.")
    else:
        user = st.session_state.current_user
        user_ref = db.collection("users").document(user)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            # Outer container for padding
            with st.container():
                st.markdown(
                    """
                    <style>
                    .profile-container {
                        padding-left: 60px;
                        padding-right: 40px;
                    }
                    </style>
                    <div class="profile-container">
                    """,
                    unsafe_allow_html=True
                )
                st.title("Profile Settings")
                col1, col2 = st.columns([1, 2])
                st.subheader("👤 Profile Picture")
                with col1:
                    current_pic = user_data.get(
                        "profile_pic",
                        "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                    )
                    st.image(current_pic, width=120, caption="Current Profile Picture")
                with col2:
                    uploaded_pic = st.file_uploader(
                        "Upload New Profile Picture",
                        type=["png", "jpg", "jpeg"]
                    )
                    if uploaded_pic is not None:
                        import base64
                        pic_bytes = uploaded_pic.read()
                        pic_b64 = base64.b64encode(pic_bytes).decode("utf-8")
                        user_ref.update({"profile_pic": f"data:image/png;base64,{pic_b64}"})
                        st.success("✅ Profile picture updated!")
                        st.stop()
                st.subheader("📝 Personal Information")
                full_name = st.text_input(
                    "Full Name",
                    value=user_data.get("full_name", "")
                )
                email = st.text_input(
                    "Email",
                    value=user_data.get("email", "")
                )
                phone = st.text_input(
                    "Phone Number",
                    value=user_data.get("phone", "")
                )
                st.markdown("""
                <div class="orange-button-wrapper">
                """, unsafe_allow_html=True)
                if st.button("Update Personal Info", key="btn_update_info"):
                    update_data = {}
                    if full_name != user_data.get("full_name", ""):
                        update_data["full_name"] = full_name
                    if email != user_data.get("email", ""):
                        update_data["email"] = email
                    if phone != user_data.get("phone", ""):
                        update_data["phone"] = phone
                    if update_data:
                        user_ref.update(update_data)
                        st.success("✅ Personal information updated!")
                        st.stop()
                    else:
                        st.info("No changes detected.")
                st.subheader("🔒 Password Management")
                current_password = st.text_input(
                    "Current Password",
                    type="password"
                )
                new_password = st.text_input(
                    "New Password",
                    type="password"
                )
                if st.button("Change Password", key="update_password"):
                    if current_password == user_data.get("password"):
                        if new_password.strip() != "":
                            user_ref.update({"password": new_password})
                            st.success("✅ Password updated successfully!")
                            st.stop()
                        else:
                            st.error("❌ New password cannot be empty.")
                    else:
                        st.error("❌ Current password is incorrect.")

                st.markdown("---")

                st.subheader("🔔 Notifications")
                email_notif = st.checkbox(
                    "Enable Email Notifications",
                    value=user_data.get("email_notif", False)
                )
                sms_notif = st.checkbox(
                    "Enable SMS Notifications",
                    value=user_data.get("sms_notif", False)
                )
                if st.button("Update Notifications", key="update_notif"):
                    notif_update = {}
                    if email_notif != user_data.get("email_notif", False):
                        notif_update["email_notif"] = email_notif
                    if sms_notif != user_data.get("sms_notif", False):
                        notif_update["sms_notif"] = sms_notif
                    if notif_update:
                        user_ref.update(notif_update)
                        st.success("✅ Notifications settings updated!")
                        st.stop()
                    else:
                        st.info("No changes detected.")

                # --- Logout Button ---
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Logout", key="logout"):
                    
                    st.session_state.logged_in = False
                    st.session_state.current_user = ""
                    st.session_state.selected = "Login/Signup"
                    st.success("✅ You have been logged out.")
                    st.rerun()
                st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                

elif st.session_state.selected == "Dashboard":
    st.title("Dashboard: Global Travel & Holidays Data")
    st.header("Interactive Power BI Dashboard")
    st.write(
        "This dashboard provides a comprehensive view of global travel data. "
        "Interact with the charts and graphs to get deeper insights into travel habits, expenditures, and popular destinations."
    )
    st.markdown("---")
    left_col, center_col, right_col = st.columns([1, 6, 1])
    with center_col:
        st.components.v1.iframe(
            "https://app.powerbi.com/reportEmbed?reportId=7186a60b-a3fe-418d-8aa8-2a4f925f3984&autoAuth=true&ctid=925b72f7-cf3c-448f-aff5-26d92b4be17c",
            width=1200,
            height=700,
            scrolling=True
        )

elif st.session_state.selected == "Feedback":
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        lottie_anim = load_lottiefile("feedback.json")  # your file name
        st_lottie(
            lottie_anim,
            speed=1,
            loop=True,
            quality="high",
            height=100,
            key="feedback_anim"
        )
        st.title("Feedback")
        st.header("We'd Love to Hear From You!")
        st.write("Please share your thoughts and suggestions to help us improve this platform.")
        name = st.text_input("Your Name", key="feedback_name")
        feedback_text = st.text_area("Your Feedback", key="feedback_text")
        if st.button("Submit Feedback"):
            db.collection("feedback").add({
                "name": name,
                "feedback": feedback_text,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.success("Thank you for your feedback!")
        

elif st.session_state.selected == "Support":
    st.title("Support")
    st.header("Contact Us for Help")
    st.write("If you encounter any issues or have questions, please reach out to our support team.")
    st.info("Email: aniketraghav05@gmail.com")
    st.info("Phone: +91-8193972190")


elif st.session_state.selected == "Settings":
    st.title("Settings")
    st.header("Customize Your Experience")
    st.markdown("""
        <style>
        .settings-box {
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #FFFFFF;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
        }
        .settings-header {
            font-size: 20px;
            font-weight: 600;
            color: #FF8C42;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="settings-box">
        <div class="settings-header">👤 Profile Settings</div>
        <input type="text" placeholder="Full Name" style="width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc;">
        <input type="text" placeholder="Email Address" style="width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc;">
        <p>Upload Profile Picture</p>
        <input type="file" style="margin-bottom: 10px;">
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class="settings-box">
            <div class="settings-header">🔔 Notifications</div>
            <input type="checkbox" id="email_notif">
            <label for="email_notif">Enable Email Notifications</label><br>
            <input type="checkbox" id="sms_notif">
            <label for="sms_notif">Enable SMS Notifications</label>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
        <div class="settings-box">
            <div class="settings-header">🎨 Appearance</div>
            <p>Choose Theme</p>
            <input type="radio" id="light" name="theme" value="Light" checked>
            <label for="light">Light</label>
            <input type="radio" id="dark" name="theme" value="Dark">
            <label for="dark">Dark</label>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="settings-box">
            <div class="settings-header">🔑 Security</div>
            <input type="password" placeholder="Change Password" style="width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc;">
            <input type="checkbox" id="2fa">
            <label for="2fa">Enable Two-Factor Authentication</label>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Save Changes"):
        st.success("Your settings have been saved successfully!")
        

elif st.session_state.selected == "Case-Study":
    st.title("Case Studies")
    st.write("Explore detailed analyses and real-world applications of global travel data.")

    # Define your case studies
    case_studies = [
        {
            "title": "Shillong Cherry Blossom Festival – Global Travel & Holidays (2024)",
            "image": "https://blog.savaari.com/wp-content/uploads/2021/11/cherry-blossom_5fb8f33489dab-1024x523.jpg",
            "summary": "A cultural festival blending music, food, and eco-tourism, attracting international visitors.",
            "link": "https://digitaldefynd.com/IQ/travel-and-tourism-marketing-case-studies/"
        },
        {
            "title": "Bali Eco-Tourism Initiative (2023)",
            "image": "https://www.taletravels.com/wp-content/uploads/2023/09/bali-waterfall.jpg",
            "summary": "Sustainable tourism efforts that increased local engagement while preserving natural habitats.",
            "link": "https://digitaldefynd.com/IQ/travel-and-tourism-marketing-case-studies/"
        }
    ]

    for cs in case_studies:
        st.markdown(
            f"""
            <div style="display:flex; background-color:white; border-radius:12px; overflow:hidden; margin-bottom:20px; height:250px;">
                <div style="flex:1; min-width:40%; max-width:40%;">
                    <img src="{cs['image']}" style="width:100%; height:100%; object-fit:cover;">
                </div>
                <div style="flex:1; padding:20px; display:flex; flex-direction:column; justify-content:center;">
                    <h3>{cs['title']}</h3>
                    <p>{cs['summary']}</p>
                    <a href="{cs['link']}" target="_blank">
                        <button style="background-color:#FF8C42; color:white; border:none; border-radius:5px; padding:10px; cursor:pointer;">
                            View Case Study
                        </button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


elif st.session_state.selected == "Blogs/News":
    
    
    st.title("Blog & News")
    tab1, tab2 = st.tabs(["News", "Blogs"])
    
    
    with tab1:
        st.header("Latest Travel Trends and Updates")
        news_items = [
             {
                "headline": "Airlines Unveil New Eco-Friendly Routes and Biometric Boarding",
                "description": "Major carriers are expanding sustainable travel options and rolling out new biometric technology to speed up the boarding process.",
                "link": "https://www.reuters.com/business/aerospace-defense/airlines-new-eco-routes-biometric-boarding-2025"
            },
            {
                "headline": "Digital Nomadism Drives Tourism Boom in Southeast Asian Capitals",
                "description": "Cities like Bangkok and Kuala Lumpur are becoming global hubs for remote workers, transforming local economies and travel trends.",
                "link": "https://www.bbc.com/travel/article/20250917-digital-nomad-boom-in-asia"
            },
            {
                "headline": "Cruise Industry Recovers with Focus on Family-Friendly Adventures",
                "description": "The cruise sector is seeing a major comeback, with new ships and itineraries catering specifically to multi-generational family vacations.",
                "link": "https://apnews.com/article/cruise-industry-recovery-family-travel-2025"
            },
            {
                "headline": "Virtual Reality is Shaping the Future of Holiday Planning",
                "description": "Travel agencies are using advanced VR technology to offer immersive destination previews, helping travelers make informed decisions.",
                "link": "https://www.forbes.com/sites/travel/2025/09/17/how-vr-is-shaping-holiday-planning"
            }
        ]

    

        # Loop through the news items and display each one in a card
        for item in news_items:
            st.markdown(
                f"""
                <div class="news-card">
                    <h4><a href="{item['link']}" target="_blank">{item['headline']}</a></h4>
                    <p>{item['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with tab2:
        st.header("Contribute a Blog Post")
        st.markdown("---")

        # Submission Form
        with st.expander("Submit a New Blog Post"):
            with st.form("blog_post_form"):
                author = st.text_input("Your Name")
                title = st.text_input("Blog Title")
                content = st.text_area("Your Blog Post Content")
                submitted = st.form_submit_button("Submit Post")
                if submitted:
                    if not all([author, title, content]):
                        st.error("Please fill all fields.")
                    else:
                        store_blog_post(author, title, content)
    
        st.header("All Blog Posts")
        st.markdown("---")

    # Display only the 2 most recent blogs
        blogs = get_blogs()
        if blogs:
            for blog in blogs:
                st.markdown(
                    f"""
                    <div class="blog-post-card">
                        <h4>{blog.get('title', 'No Title')}</h4>
                        <p><i>By: {blog.get('author', 'Anonymous')}</i></p>
                        <p>{blog.get('content', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No blog posts submitted yet.")


if st.session_state.get("show_ai", False):
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: white !important;
            color: black;
            position: relative;
        }
        /* Close button styling */
        .close-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #FF8C42;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.sidebar:
        # Custom HTML for close button
        close_clicked = st.button("✖️", key="ai_close")
        if close_clicked:
            st.session_state["show_ai"] = False
        
        st.markdown(
            '<div style="background-color:#FF6600;color:white;padding:10px;border-radius:10px;font-weight:bold;">'
            'Hi! I’m <b>Voya AI</b>, available 24x7. Ask me anything!</div>',
            unsafe_allow_html=True,
        )

       
        last_user, last_ai = st.session_state.get("latest", ("", ""))
        if last_user:
            st.markdown(f"<div style='background:#E6F2FF;color:black;padding:8px;border-radius:8px;margin-bottom:8px;'>You: {last_user}</div>", unsafe_allow_html=True)
        if last_ai:
            st.markdown(f"<div style='background:#F0F0F0;color:black;padding:8px;border-radius:8px;margin-bottom:8px;'><b>Voya AI:</b> {last_ai}</div>", unsafe_allow_html=True)

       
        with st.form("chat_form"):
            user_input = st.text_input("Type your message here:", key="ai_input")
            submitted = st.form_submit_button("Send")
            if submitted and user_input:
                placeholder = st.empty()  
                placeholder.markdown(f"Voya AI: Thinking...", unsafe_allow_html=True)
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": user_input}],
                        temperature=0.7,
                        max_tokens=150
                    )
                    ai_text = response.choices[0].message.content
                except Exception as e:
                    ai_text = f"Error: {e}"
                st.session_state.latest = (user_input, ai_text)
                placeholder.markdown(f"Voya AI: {ai_text}", unsafe_allow_html=True)


