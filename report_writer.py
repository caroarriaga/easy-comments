# example/st_app.py

import streamlit as st
import streamlit_pills as stp
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
from openai import OpenAI

with st.sidebar:
    spreadsheet_link=st.text_input(label="Google sheet link", placeholder="Paste link here")

if spreadsheet_link:
    conn = st.connection("gsheets", type=GSheetsConnection)

    data = conn.read(spreadsheet=spreadsheet_link, usecols=[1,2,3,4,5])
    df=pd.DataFrame(data)
    df=df.iloc[1:]
    df.columns = ['T1','T2','firstName','lastName','general']
    df['firstName'].replace('', np.nan, inplace=True)
    df.dropna(subset=['firstName'],inplace=True)
    df.fullname=df[['firstName','lastName']].agg(' '.join, axis=1)

    class_name = df.general.unique()[0]

    st.write(f"Class name: {class_name}")

    nameCol,ratCol,gradeCol= st.columns([3,2,2])

    with nameCol:
        st.subheader("Student")
        student=st.selectbox("Select a student", df.fullname)
        firstName=df.loc[df.fullname==student].firstName.values[0]

    with ratCol:
        # Expectations
        st.subheader("Expectations")
        expectations=st.multiselect(label="Overall Expectations", options=["Not met","Minimal","Met"])

    with gradeCol:
        
        # Grade Improvement
        if df.loc[df.fullname==student].T1.values[0]==None:
            quant_improvement=0
            grade=df.loc[df.fullname==student].T1.values[0]
            st.metric(label="Term grade", value=grade ,delta=quant_improvement)
            
        else:
            quant_improvement=(df.loc[df.fullname==student].T2.values[0]-df.loc[df.fullname==student].T1.values[0])*100/df.loc[df.fullname==student].T1.values[0]
            quant_improvement=quant_improvement.round(2)
            grade=df.loc[df.fullname==student].T2.values[0]
            st.metric(label="Term grade", value=grade, delta=quant_improvement)




    # Assignments
    st.subheader("Google Classroom assignments")

    exp1,exp2,exp3 = st.columns([2,1,1])
    with exp1:
        ## Completion
        completion=stp.pills(label="Assignment completion", options=["None", 
                                                            "Missing several", 
                                                            "Missing some",
                                                            "Completed all"])

    with exp2:
        special_feed_completion=stp.pills(label="Special feedback", options=["thoughtful and thorough", 
                                                            "needs support with coursework", 
                                                            "late submissions",
                                                            "Review written work"])

    with exp3:
        corrective_completion=stp.pills(label="Corrective actions", options=["attend FIT block", 
                                                            "submit on time", 
                                                            "submit missing asignments"])

    st.subheader("Lab performance")
    activity_name=st.text_input("Special activity name:")

    workshop_completion=stp.pills(label="Lab feedback", options=[f"thoughtful and thorough", 
                                                        "partial completion (meal)",
                                                        "partial completion (design)", 
                                                        "Incomplete most assessment",
                                                        ])


    # behavior
    st.subheader("Behavior")
    beh1, beh2, beh3=st.columns([3,3,3])
    with beh1:
        behavior_lab=stp.pills(label="Lab behavior feedback", options=["Good progress",
                                                            "Some progress",
                                                            "No progress"
                                                            ])

    with beh2:
        skills=st.multiselect(label="Skill development",options=["teamwork",
                                    "kitchen safety promoter",
                                    "sanitation promoter",
                                    "participates in class"
                                    "avoids participation",
                                    "lack of focus",
                                    "punctual to class",
                                    "late to class",
                                    "uses cellphone in class",

                                    ]
                            )

    with beh3:
        kitchen_maintenance=st.multiselect("Kitchen behavior to reinforce", ["cleans up as they go", 
                                                                "assists with folding and putting away laundry",
                                                                "takes out the recycling",
                                                                "sweeps the classroom floor.", 
                                                                "cooking and kitchen clean up at home"])

    # Attendance
    st.subheader("Attendance feedback")
    at1,at2=st.columns([4,4])
    with at1:
        attendance=stp.pills(label="Attendance feedback", options=["attends class consistently.", 
                                                            "Inconsistent attendance.",
                                                            "No attendance",
                                                            ])

    with at2:
        punctuality=st.multiselect(label="Punctuality feedback", options=["Excellent", 
                                                            "Sometimes late to class",
                                                            "Sometimes leaves during class time",
                                                            "Frequently late to class",
                                                            "Frequently leaves during class time"
                                                            ])
        
    custom_comment=st.text_input("General notes:")

    feedbackList=[f"Overall expectations rating: {expectations}",f"Assignment completion rating: {completion}",f"feedback pertaining assignments:{special_feed_completion}",
                  f"Corrective actions for future assignments: {workshop_completion}",f"Behavior during the kitchen lab {behavior_lab}",
                  f"skills development shown: {skills}", f"behavior to reinforce: {kitchen_maintenance}",custom_comment,
                  f"Regarding attendance: {attendance}",f"Regarding puntuality:{punctuality}",f"{firstName} grade was {grade} and had a change of {quant_improvement}"]

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


    if st.button("Create commentary"):
        # Define the user prompt message
        prompt = f"Create a feedback summary for {firstName}, here's all her feedback:{feedbackList}"
        # Create a chatbot using ChatCompletion.create() function
        completion = client.chat.completions.create(model='gpt-3.5-turbo', messages=[
            {"role": "system", "content": "You are a helpful teacher assistant. I will give you a list of feedback in the following areas: Expectation, Assignments, Behavior, and Attendance pertaining the student {firstName}. You will create a concise personalized summary about {firstName} performance and ways to improve and you must include a comment regarding her grade and change compared to last term."},
            {"role": "user", "content": prompt}
        ])
        msg = completion.choices[0].message.content

        st.write(msg)
else:
    st.sidebar.markdown("To create commentaries please paste a google sheet above. Make sure it can be shared anyone with the link.")
    




