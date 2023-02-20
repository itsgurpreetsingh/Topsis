import sys
import pandas as pd
import math as m
import warnings
from pandas.api.types import is_numeric_dtype
import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import re
warnings.filterwarnings("ignore")
##Error Handling
#For checkin no of parameters in command line argument 

st.title("TOPSIS CALCULATOR")
with st.form("my_form"):
    weights=st.text_input("Enter weights") 
    impacts=st.text_input("Enter impacts")
    resFileName = st.text_input("Enter name of result file")
    mailid=st.text_input("Enter Email Id (in small letters)") 
    input_file = st.file_uploader("Choose a file")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("text_input", weights, "text_input", impacts,"text_input",resFileName,"text_input",mailid)
        #For checking valid entry and comma separation of    
        try:
            weights=weights.split(',')  
            numbers = [int(x.strip()) for x in weights]
            impacts=impacts.split(',')  
            characters=[str(x.strip()) for x in impacts]
        except:
            st.error('Please enter weights with only numbers separated by commas ')
            st.stop()

        for i in impacts:
            if i not in ['+','-']:
                st.error("Please enter valid impact '+' or '-' separated by commas")
                st.stop()
        try:
            df=pd.read_csv(input_file)
        except:
            st.error("File not found") 
            st.stop()
        testEmail = mailid
        testEmail=testEmail.strip()
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'    
        if(re.search(regex,testEmail)):   
            print("valid") 
        else:   
            st.error("Invalid email address" )
            st.stop()   
        finalData=df
        if((df.columns.size-1)<3):
            st.error("Less no of columns in input file")
            st.stop()
        elif(((df.columns.size-1)!=len(weights))&((df.columns.size-1)!=len(impacts))):  
            st.error("Weights,impacts are not equal to no of columns")
            st.stop()
        if(df.columns.size-1>len(weights)):
            st.error("Insufficient number of weights are entered")
            st.stop()
        elif(df.columns.size-1>len(impacts)):
            st.error("Insufficient number of impacts are entered")
            st.stop()
        elif(df.columns.size-1<len(weights)):
            st.error("More than required number of weights are entered")
            st.stop()
        elif(df.columns.size-1<len(impacts)) :
            st.error("More than required number of impacts are entered")
            st.stop()
        noOfColumns=df.axes[1]
        colNames=list(df.columns)
        colNames.pop(0)
        df=df[colNames]

        for i in colNames:
            if(is_numeric_dtype(df[i])==False):
                st.error("Input File contains non numeric data")
                st.stop()
        st.write('Result is under process, Please wait...')   
        sqrSum={}
        idealBest={}
        idealWorst={}
        idealBestDistance=[]
        idealWorstDistance=[]
        perfScore=[]
        ranking={}
        rank=[]
        def rootSquareSum(value):
            sum=0
            for i in value:
                sum=sum+(i*i)
            return m.sqrt(sum)

        def normalization(value):
            for i in colNames:
                df[i]=df[i]/value[i]      

        ##For normalization
        for i in colNames:
            sqrSum[i]=rootSquareSum(df[i])

        normalization(sqrSum)


        ##weight assignment
        weights=[int(i) for i in weights]
        index=0

        for i in colNames:
            df[i]=df[i]*weights[index]
            index=index+1

        ##finding ideal best and ideal worst
        indexImpact=0      
        for i in colNames:
            if impacts[indexImpact]=='-':
                idealBest[i]=min(df[i])
                idealWorst[i]=max(df[i])
                indexImpact=indexImpact+1
            else:
                idealBest[i]=max(df[i])    
                idealWorst[i]=min(df[i])
                indexImpact=indexImpact+1   
    
        ##finding ideal best and ideal worst distance
        for i in df.index:
            sum=0
            for j in colNames:
                sum=sum+m.pow((df[j][i]-idealBest[j]),2)
            idealBestDistance.append(m.sqrt(sum))    

        for i in df.index:
            sum=0
            for j in colNames:
                sum=sum+m.pow((df[j][i]-idealWorst[j]),2)
            idealWorstDistance.append(m.sqrt(sum))   

        #finding performance score
        for i in df.index:
            perfScore.append(idealWorstDistance[i]/(idealBestDistance[i]+idealWorstDistance[i]))

        finalData["Topsis Score"]=perfScore

        ##finding rank
        sortedScore=sorted(perfScore,reverse=True)
        for i in range(0,len(sortedScore)):
            ranking[sortedScore[i]]=i
        for j in perfScore:
            rank.append(ranking[j]+1)
        finalData['Rank']=rank
        finalData.to_csv(resFileName,index=False)
        st.write(finalData)
        st.write('Sending result on Email...')
        fromaddr = "gsingh102003@gmail.com"
        toaddr = mailid
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Topsis Result"
        body = "Topsis Result"
        msg.attach(MIMEText(body, 'plain'))
        attachment = open(resFileName, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
  
        # encode into base64
        encoders.encode_base64(p)
   
        p.add_header('Content-Disposition', "attachment; filename= %s" % resFileName)
  
        # attach the instance 'p' to instance 'msg'
        msg.attach(p)
  
         # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com',587)
  
        # start TLS for security
        s.starttls()
  
        # Authentication
        s.login(fromaddr, "erbaazraounsrsqp")
  
        # Converts the Multipart msg into a string
        text = msg.as_string()
  
        # sending the mail
        s.sendmail(fromaddr, toaddr, text)
  
        # terminating the session
        s.quit()
        st.success("Result successfully sent on mail") 
        input_file.seek(0)
        os.remove(resFileName)  




