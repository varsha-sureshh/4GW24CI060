import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import utils
from PIL import Image
import datetime

st.set_page_config(page_title="Automated Resume Builder", layout="centered")

st.title("Automated Resume Builder")
st.write("Fill the form. Only **Name**, **LinkedIn** and **Education** are required. Everything else is optional.")

# --- Helper functions for dynamic lists via session_state ---
if "edu_count" not in st.session_state:
    st.session_state.edu_count = 3  # default education blocks
if "intern_count" not in st.session_state:
    st.session_state.intern_count = 1
if "proj_count" not in st.session_state:
    st.session_state.proj_count = 2

def add_edu():
    st.session_state.edu_count += 1

def remove_edu():
    if st.session_state.edu_count > 1:
        st.session_state.edu_count -= 1

def add_intern():
    st.session_state.intern_count += 1

def remove_intern():
    if st.session_state.intern_count > 0:
        st.session_state.intern_count -= 1

def add_proj():
    st.session_state.proj_count += 1

def remove_proj():
    if st.session_state.proj_count > 0:
        st.session_state.proj_count -= 1

# --- Top-level personal info ---
st.subheader("Personal Info")
col1, col2 = st.columns([3,1])
with col1:
    name = st.text_input("Full name *", value="").strip()
    contact = st.text_input("Contact number")
    email = st.text_input("Email")
    github = st.text_input("GitHub URL")
    linkedin = st.text_input("LinkedIn URL *", value="").strip()
    address = st.text_input("Address / Location")
with col2:
    st.write("Profile photo (optional)")
    photo_file = st.file_uploader("Upload photo (jpg/png)", type=["jpg","jpeg","png"], accept_multiple_files=False)
    if photo_file:
        img = Image.open(photo_file)
        st.image(img, use_column_width=True, caption="Profile photo preview")

st.subheader("Career Objective")
career_obj = st.text_area("Career Objective (optional)", height=80)

# --- Education repeated blocks ---
st.subheader("Education * (At least one entry required)")
edu_col1, edu_col2 = st.columns([1,1])
with edu_col1:
    st.button("Add education", on_click=add_edu)
with edu_col2:
    st.button("Remove education", on_click=remove_edu)

educations = []
for i in range(st.session_state.edu_count):
    st.markdown(f"**Education #{i+1}**")
    deg = st.text_input(f"Degree / Program (Education {i+1})", key=f"deg_{i}")
    inst = st.text_input(f"Institution (Education {i+1})", key=f"inst_{i}")
    loc = st.text_input(f"Location (Education {i+1})", key=f"loc_{i}")
    cgpa = st.text_input(f"CGPA / Percentage (Education {i+1})", key=f"cgpa_{i}")
    start = st.text_input(f"Start year (YYYY) (Education {i+1})", key=f"start_{i}")
    end = st.text_input(f"End year / Grad year (YYYY) (Education {i+1})", key=f"end_{i}")
    if deg or inst or cgpa or start or end:
        educations.append({
            "degree": deg.strip(),
            "institution": inst.strip(),
            "location": loc.strip(),
            "cgpa": cgpa.strip(),
            "start": start.strip(),
            "end": end.strip()
        })

# --- Skills, Interests, Languages ---
st.subheader("Skills, Interests & Languages")
skills = st.text_area("Skills (comma separated or newline separated)")
interests = st.text_area("Interests / Hobbies")
languages_known = st.text_input("Languages known (comma separated)")

# --- Internships repeated blocks ---
st.subheader("Internships (optional, will be sorted newest → oldest)")
int_col1, int_col2 = st.columns([1,1])
with int_col1:
    st.button("Add internship", on_click=add_intern)
with int_col2:
    st.button("Remove internship", on_click=remove_intern)

internships = []
for i in range(st.session_state.intern_count):
    st.markdown(f"**Internship #{i+1}**")
    org = st.text_input(f"Organization / Title (Intern {i+1})", key=f"org_{i}")
    desc = st.text_area(f"Short description (Intern {i+1})", key=f"idesc_{i}", height=60)
    start = st.text_input(f"Start (e.g. Feb 2025) (Intern {i+1})", key=f"istart_{i}")
    end = st.text_input(f"End (e.g. Jul 2025 or Ongoing) (Intern {i+1})", key=f"iend_{i}")
    if org or desc or start or end:
        internships.append({
            "org": org.strip(),
            "desc": desc.strip(),
            "start": start.strip(),
            "end": end.strip()
        })

# --- Projects repeated blocks ---
st.subheader("Projects (optional)")
proj_col1, proj_col2 = st.columns([1,1])
with proj_col1:
    st.button("Add project", on_click=add_proj)
with proj_col2:
    st.button("Remove project", on_click=remove_proj)

projects = []
for i in range(st.session_state.proj_count):
    st.markdown(f"**Project #{i+1}**")
    title = st.text_input(f"Project title (Proj {i+1})", key=f"ptitle_{i}")
    pdesc = st.text_area(f"Short description (Proj {i+1})", key=f"pdesc_{i}", height=60)
    tech = st.text_input(f"Language / Frameworks used (Proj {i+1})", key=f'ptech_{i}')
    if title or pdesc or tech:
        projects.append({
            "title": title.strip(),
            "desc": pdesc.strip(),
            "tech": tech.strip()
        })

# --- Export filename option ---
st.subheader("Export options")
export_name_default = (name.replace(" ", "_") if name else "resume")
export_filename = st.text_input("Export filename (without .pdf)", value=export_name_default)

# --- Validation & Generate PDF ---
def safe_int_year(y):
    try:
        return int(y)
    except:
        return None

def generate_pdf_bytes(data):
    """Creates the PDF bytes using reportlab and returns BytesIO."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # points
    margin = 30 * mm

    # Helper for wrapping text
    from reportlab.lib.utils import simpleSplit

    # Coordinates: we'll follow the layout similar to the template
    x_left = margin
    x_right_img = width - margin - 60*mm  # where profile image begins
    y = height - margin

    # Name
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x_left, y, data.get("name", "").upper() if data.get("name") else "")
    # Draw horizontal line under header
    y -= 12
    c.setLineWidth(0.8)
    c.line(margin, y, width - margin, y)

    # Left column contact details
    y -= 18
    c.setFont("Helvetica", 9)
    contact_lines = []
    if data.get("contact"):
        contact_lines.append(data["contact"])
    if data.get("email"):
        contact_lines.append(data["email"])
    if data.get("github"):
        contact_lines.append(data["github"])
    if data.get("linkedin"):
        contact_lines.append(data["linkedin"])
    if data.get("address"):
        contact_lines.append(data["address"])

    for line in contact_lines:
        if y < margin + 200:
            c.showPage()
            y = height - margin
        c.drawString(x_left, y, line)
        y -= 12

    # Profile photo on the right (approx top-right)
    if data.get("photo"):
        try:
            pil_img = data["photo"]
            # ensure orientation / sizing
            max_w = 60*mm
            max_h = 60*mm
            pil_img.thumbnail((max_w, max_h), Image.ANTIALIAS)
            img_io = BytesIO()
            pil_img.save(img_io, format="PNG")
            img_io.seek(0)
            img_reader = ImageReader(img_io)
            # place top-right aligned
            img_w, img_h = pil_img.size
            # convert px->points roughly using 72 dpi default; PIL size in px -> scale proportional
            # easier: use reportlab drawImage with width/height in points
            draw_w = max_w
            draw_h = (img_h / img_w) * draw_w if img_w != 0 else max_h
            c.drawImage(img_reader, x_right_img, height - margin - draw_h + 10, width=draw_w, height=draw_h, preserveAspectRatio=True)
        except Exception as e:
            # ignore image errors
            pass

    # Move down before next section
    y -= 8

    # Career Objective section
    if data.get("career_obj"):
        y -= 6
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "CAREER OBJECTIVE")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        c.setFont("Helvetica", 9)
        wrapped = simpleSplit(data["career_obj"], "Helvetica", 9, width - 2*margin)
        for line in wrapped:
            if y < margin + 100:
                c.showPage()
                y = height - margin
            c.drawString(x_left, y, line)
            y -= 12
        y -= 4

    # EDUCATION section (required)
    if data.get("educations"):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "EDUCATION")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        c.setFont("Helvetica-Bold", 9)
        # educations are already sorted newest->oldest
        for edu in data["educations"]:
            deg_inst = f"{edu.get('degree','')} - {edu.get('institution','')}".strip(" -")
            loc = edu.get("location", "")
            dates = ""
            if edu.get("start") or edu.get("end"):
                dates = f"{edu.get('start','')} - {edu.get('end','')}".strip(" -")
            cgpa = edu.get("cgpa", "")
            # Left: degree+institution; Right: CGPA/dates
            if y < margin + 80:
                c.showPage()
                y = height - margin
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_left, y, deg_inst)
            # draw cgpa/dates on right side
            right_text = cgpa if cgpa else dates
            if right_text:
                c.setFont("Helvetica", 9)
                text_w = c.stringWidth(right_text, "Helvetica", 9)
                c.drawString(width - margin - text_w, y, right_text)
            y -= 12
            # institution/location line or extra desc if any
            c.setFont("Helvetica-Oblique", 8)
            inst_line = loc
            if inst_line:
                c.drawString(x_left, y, inst_line)
                y -= 12
            else:
                y -= 2

    # SKILLS
    if data.get("skills"):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "SKILLS")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        c.setFont("Helvetica", 9)
        wrapped = simpleSplit(data["skills"], "Helvetica", 9, width - 2*margin)
        for line in wrapped:
            if y < margin + 60:
                c.showPage()
                y = height - margin
            c.drawString(x_left, y, line)
            y -= 12
        y -= 4

    # INTERNSHIPS
    if data.get("internships"):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "INTERNSHIP")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        c.setFont("Helvetica-Bold", 9)
        for intern in data["internships"]:
            # org on left, date(s) on right
            org_line = intern.get("org","")
            dates = f"{intern.get('start','')} - {intern.get('end','')}".strip(" -")
            if y < margin + 100:
                c.showPage()
                y = height - margin
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_left, y, org_line)
            if dates:
                c.setFont("Helvetica", 9)
                text_w = c.stringWidth(dates, "Helvetica", 9)
                c.drawString(width - margin - text_w, y, dates)
            y -= 12
            # description
            desc = intern.get("desc","")
            if desc:
                c.setFont("Helvetica", 9)
                wrapped = simpleSplit(desc, "Helvetica", 9, width - 2*margin)
                for line in wrapped:
                    if y < margin + 60:
                        c.showPage()
                        y = height - margin
                    c.drawString(x_left + 6, y, line)
                    y -= 12
            y -= 6

    # PROJECTS
    if data.get("projects"):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "PROJECTS")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        for proj in data["projects"]:
            title = proj.get("title","")
            desc = proj.get("desc","")
            tech = proj.get("tech","")
            if y < margin + 100:
                c.showPage()
                y = height - margin
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_left, y, title)
            y -= 12
            if desc:
                c.setFont("Helvetica", 9)
                wrapped = simpleSplit(desc, "Helvetica", 9, width - 2*margin)
                for line in wrapped:
                    if y < margin + 60:
                        c.showPage()
                        y = height - margin
                    c.drawString(x_left + 6, y, line)
                    y -= 12
            if tech:
                if y < margin + 30:
                    c.showPage()
                    y = height - margin
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(x_left + 6, y, f"Technology Used: {tech}")
                y -= 12
            y -= 6

    # INTERESTS & LANGUAGES
    if data.get("interests"):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "INTERESTS")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        c.setFont("Helvetica", 9)
        wrapped = simpleSplit(data["interests"], "Helvetica", 9, width - 2*margin)
        for line in wrapped:
            if y < margin + 40:
                c.showPage()
                y = height - margin
            c.drawString(x_left, y, line)
            y -= 12
        y -= 4

    if data.get("languages"):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_left, y, "LANGUAGES KNOWN")
        y -= 6
        c.setLineWidth(0.5)
        c.line(x_left, y, width - margin, y)
        y -= 12
        c.setFont("Helvetica", 9)
        c.drawString(x_left, y, data["languages"])
        y -= 12

    # footer small print date
    today = datetime.date.today().strftime("%d %b %Y")
    c.setFont("Helvetica", 7)
    c.drawString(margin, 12, f"Generated: {today}")

    c.save()
    buffer.seek(0)
    return buffer

# Validate mandatory fields
generate = st.button("Generate & Download PDF")
if generate:
    errors = []
    if not name:
        errors.append("Name is required.")
    if not linkedin:
        errors.append("LinkedIn is required.")
    if len(educations) == 0:
        errors.append("At least one Education entry is required.")

    if errors:
        st.error("Please fix the following: " + " ".join(errors))
    else:
        # Sort education by end year descending (if parseable), else keep order but push empties last
        def edu_sort_key(e):
            y = safe_int_year(e.get("end","") or "")
            return -(y or 0)
        educations_sorted = sorted(educations, key=edu_sort_key)

        # sort internships by end year if possible
        def intern_sort_key(i):
            # try to extract last 4-digit year from end field
            end = i.get("end","")
            # attempt to find 4-digit year inside string
            import re
            m = re.search(r"(\d{4})", end)
            if m:
                return -int(m.group(1))
            return 0
        internships_sorted = sorted(internships, key=intern_sort_key)

        # Prepare image as PIL Image if exists
        pil_photo = None
        if photo_file:
            try:
                pil_photo = Image.open(photo_file).convert("RGB")
            except:
                pil_photo = None

        pdf_buffer = generate_pdf_bytes({
            "name": name,
            "contact": contact,
            "email": email,
            "github": github,
            "linkedin": linkedin,
            "address": address,
            "career_obj": career_obj,
            "educations": educations_sorted,
            "skills": skills,
            "internships": internships_sorted,
            "projects": projects,
            "interests": interests,
            "languages": languages_known,
            "photo": pil_photo
        })

        fname = (export_filename.strip() or "resume") + ".pdf"
        st.success("PDF generated — click to download.")
        st.download_button("Download PDF", data=pdf_buffer, file_name=fname, mime="application/pdf")
