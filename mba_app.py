import streamlit as st
import pandas as pd
import random
import os
import matplotlib.pyplot as plt
import plotly.express as px
random.seed(0)


#######################################################################
#######################################################################

def get_rank(i, firm_name, df, id):
    return int(df[df[id] == i].iloc[0,:][firm_name])


def arrange(df, scoring_variable, id, number_of_sessions, maximum, start):
    # file_name = input('File name: ') # filename   
    # scoring_variable = input('Rank variable (enter random for random): ') # 
    # id = input('Student ID column (has to be unique): ') # email, column number
    # number_of_sessions = int(input("Number of sessions: ")) + 1 # 4, 5, 6, 7, 8 (4 to 10)
    # maximum = int(input('Maximum number of students per session: ')) # 1 to 15
    # start = input("Bidding data start from column: ")  # company 
    
    #df = pd.read_csv(file_name)
    number_of_sessions += 1
    df['random'] = [random.randrange(0, 1) for i in range(len(df))]
    start = list(df).index(start)
    df = df.sort_values(scoring_variable).drop("random", axis=1).reset_index(drop=True)
    company_list = list(df)[start:]

    classmates = {}
    for index, row in df.iterrows():
        classmates[row[id]] = []
    company = {}

    for i in list(df)[start:]:
        company[i] = []
        for j in range(number_of_sessions - 1):
            company[i].append([])

    for company_per_classmates in range(1, number_of_sessions):
        for i in range(1, len(company) + 1):
            for row_num in range(df.shape[0]):
                data = df.iloc[row_num, :]
                chosen_company = company_list[list(data.values[start:]).index(i)]
                sid = data.loc[id]

                if len(classmates[sid]) < company_per_classmates:
                    if len(company[chosen_company][len(classmates[sid])]) < maximum and chosen_company not in classmates[sid]:
                        company[chosen_company][len(classmates[sid])].append(sid)
                        classmates[sid].append(chosen_company)
                row_num += 1
    cols = []
    for i in range(1, number_of_sessions):
        cols += ['Firm' + str(i), 'Rank' + str(i)]
    student_result = pd.DataFrame(columns=list(df)[:start] + cols)

    row_num = 0
    for i in classmates:
        result = df[df[id] == i].values.tolist()[0][:start]
        for firm_num in range(len(classmates[i])):
            result += [classmates[i][firm_num], get_rank(i, classmates[i][firm_num], df, id)]
        result += [' ', ' '] * (number_of_sessions - len(classmates[i]) - 1)
        student_result.loc[row_num] = result
        row_num += 1

    cols = []
    for i in range(maximum):
        cols.append('Student' + str(i + 1))
    company_result = pd.DataFrame(columns=['Company', 'Round', 'Number of students'] + cols)
    loc = 0
    for i in company:
        for j in range(len(company[i])):
            result = [i, str(j + 1), str(len(company[i][j]))] + company[i][j] + [' '] * (maximum - len(company[i][j]))
            company_result.loc[loc] = result
            loc += 1
    student_result.to_csv("student_result.csv", index=False)
    company_result.to_csv("company_result.csv", index=False)
    return student_result, company_result



#####################################################################
#####################################################################

st.title("MBA USC APP")
st.write("Welcome!")


# Create a file uploader component
file_name = st.file_uploader("Upload a CSV file", type=["csv"])

# Check if a file was uploaded
if file_name is not None:
    st.write("File Uploaded!")

    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_name)

    # Display the DataFrame
    st.write("Data Preview:")
    st.write(df)

    # Create six drop-down menus with unique labels and options
    scoring_variable = st.selectbox("Choose the scoring variable", ["random"])
    id = st.selectbox("Choose studentID columns", [i for i in df.columns])
    number_of_sessions = st.selectbox("Number of Sessions", [i for i in range(0,11)])
    maximum = st.selectbox("Maximum number of students per session", [i for i in range(16)])
    start = st.selectbox("bidding data start from column", [i for i in df.columns])


    if st.button("Generate DataFrames"):
        df1, df2 = arrange(df, scoring_variable, id, number_of_sessions, maximum, start)
        st.success("DataFrames generated!")

        sessions = [i+1 for i in range(number_of_sessions)]
        lst = ['First Name']
        for i in sessions:
            lst.append("Firm" + str(i))
        final = df1[lst]
        #final
        st.subheader("Student Result")
        st.write(final, use_container_width=True)



        st.subheader("Company Result")
        st.write(df2, use_container_width=True)

        st.download_button("Donwload Student Result CSV File",
                           df1.to_csv(index=False),
                           file_name='student_result.csv',
                           mime = 'text/csv')
        

        st.download_button("Donwload Company Result CSV File",
                    df2.to_csv(index=False),
                    file_name='company_result.csv',
                    mime = 'text/csv')
        

        # Students Placed 
        # ToDo: Debug
        # st.subheader("Student Placement")
        # dict2 = {}

        # for j in range(number_of_sessions):
        #     total_num = 0
        #     for z in range(maximum):
        #         for i in df2[df2['Round'] == j+1].to_dict('list')[f'Student{z+1}']:
        #             if i not in [' ', '']:
        #                 total_num += 1
            
        #     dict2[j+1] = total_num

        # st.write(dict2)

        # for k,v in dict2.items():
        #     st.write(f"Round {k}. Number of students placed: {v}")

        ###########################


        # Chart Company
        # st.subheader("Analytics")
        # fig, ax = plt.subplots(figsize=(12,8))
        # ax.bar(df2['Company'], df2['Number of students'])
        # plt.title("Company Result")
        # plt.xticks(rotation=90)
        # ax.tick_params(axis='both', labelsize=14) 
        # ax.set_xlabel('Company', fontsize=16)  # Change 16 to your desired font size
        # ax.set_ylabel('Number of Students', fontsize=16)  # Change 16 to your desired font size
        # st.pyplot(fig)

        # Create a bar plot using Plotly Express
        
        df2['company_short'] = [i.split('-')[0] for i in df2['Company'].tolist()] # shorting company name
        fig = px.bar(df2, x='company_short', y='Number of students', color='Round')

        # Customize the plot
        fig.update_layout(
            title='Number of Students',
            xaxis_title='Company',
            yaxis_title='Number of Students',
            width=800,  # Adjust the width as needed
            height=600  # Adjust the height as needed
        )

        # Show the plot
        st.plotly_chart(fig)


        
