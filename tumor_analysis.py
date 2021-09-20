import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np
from pandas.core.reshape.concat import concat 
import streamlit as st 
import os

class DataGroup : 
    def __init__(self, name, timepoint, dataframe):
       self.name = name
       self.timepoint = timepoint
       self.dataframe = pd.DataFrame(data= dataframe)
    
    #Function to rename datatype parsing to dataframe (e.g. Tumor Area, Vascular Leak, etc.)
    def rename_dataframe(self, datatype, dataframe): 
        dataframe = self.dataframe
        dataframe = dataframe.rename(datatype)
        return dataframe

     #Function to calculate mean raw tumor area in pixel unit
    def calculateAvg(self, dataframe):
        dataframe = self.dataframe
        avg = dataframe.mean()
        return avg
    
    #Function to calculate standard deviation of tumor area in pixel unit
    def calculateSD(self, dataframe):
        dataframe = self.dataframe
        std = dataframe.std()
        return std

    #Function to calculate SEM of tumor area in pixel unit 
    def calculateSEM(self, dataframe):
        dataframe = self.dataframe
        sem = dataframe.sem()
        return sem

# Create a new class of DataGroup to store data
class DataSeries :

    #Initiate a Data object contains a name, timepoint, and a PANDAS series that takes  
    # raw tumor area from CellProfiler output .csv file 
    def __init__(self, name, timepoint, df):
        self.name = name 
        self.timepoint = timepoint
        self.df = pd.Series(data = df)
        self.df = self.df.rename('Value' + timepoint) 
    
    #Function to calculate mean raw tumor area in pixel unit
    def calculateAvg(self, df):
        df = self.df
        avg = df.mean()
        return avg
    
    #Function to calculate standard deviation of tumor area in pixel unit
    def calculateSD(self, df):
        df = self.df 
        std = df.std()
        return std

    #Function to calculate SEM of tumor area in pixel unit 
    def calculateSEM(self, df):
        df = self.df 
        sem = df.sem()
        return sem

#ReadMe function 
def ReadMe() : 
    
    st.markdown("""**Instructions:**  
    1. Type name of condition to be analyzed. (e.g. _Control_ or _Bevacizumab-100ng/mL_)  
    2. Indicate numbers of time points to be analyzed (e.g. 5 timepoint for 0h to 96h).  
    3. Type name of timepoint to be analyzed and upload its CellProfiler .csv file.   
    3. This app will automatically display a table summary of raw tumor area data and calculate __Mean/SD/SEM/N.__ In addition, it will also normalize raw data to T-0h and display __%Change/SD/SEM/N.__  
    4. Save your data tables to .csv files and export to your graphing app (e.g. Prism) or use Plot Data mode for quick data visualization.  
    5. Use your normalized summary .csv output files (i.e. condition_normalized summary.csv) in Plot Data mode.  """)

def ExtractData() : 
    datalist = []
    namelist = []
    savefile_key = 'savefile_'

    st.header('Extract Data')
    st.write("""__Instructions:__   
    1. Indicate number of groups in this dataset, according to your keylist.    
    2. List name of groups in this dataset according to your keylist, separated each by a comma (e.g. 100_PFU_mL, 300_PFU_mL).     
    3. Type in _name_ of the timepoint associated with this dataset (e.g. 0h, 24h, 48h). This will be used to label dataframe later.  
    4. Upload your dataset _*_Image.csv_ file from CellProfiler pipeline.   
    5. Type in directory path to save raw .csv files after sorting by groups. (e.g. _/Users/a/Desktop/data/_)  
    """)

    num_condition = st.text_input('Number of groups in this dataset, according to your keylist:')
    name_input = st.text_input('List name of groups in this dataset according to your keylist, separated each by a comma (e.g. 100_PFU_mL, 300_PFU_mL):')
    namelist = name_input.split(', ')

    timepoint_input = st.text_input("Timepoint associated with this dataset:")

    uploaded_file = st.file_uploader("Upload your CellProfiler *_Image.csv file:")
    uploaded_dataframe = pd.read_csv(uploaded_file, header= 0, index_col= 'Metadata_Key_Group')
    save_dir = st.text_input('Type directory to save raw data .csv files sorted by groups:')

    st.write('___')
    st.write("""## _Raw Data Sorted By Groups_  """)
    for i in range(0,int(num_condition)) :
        condition_dataframe = uploaded_dataframe.loc[namelist[i]]
        dataObj = DataGroup(namelist[i], timepoint_input, condition_dataframe)
        datalist.append(dataObj)

        st.write(datalist[i].dataframe)
        raw_csv = os.path.join(save_dir, namelist[i] + '_' + timepoint_input + '_raw_data.csv')
        saved = st.button('Save ' + namelist[i] + '_' + timepoint_input + '_raw_data.csv file', key= savefile_key + str(i))
        if saved:
            datalist[i].dataframe.to_csv(raw_csv)
            st.write('_Files saved_') 


#Analyze tumor growth function  
def AnalyzeData() :
    datapoint = []
    filenamelist = []

    #Collect condition name and number of timepoints
    with st.container() :
        group_name = st.sidebar.text_input('Name of condition:')
        datapoint_input = st.sidebar.text_input('Number of timepoint(s) in time course:') 

    st.header('Analyze Data')
    st.write("""__Instructions:__   
    1. Type in name your condition. (__Note:__ Avoid using special characters when naming. For example, replace "_10,000 RFU/mL_" with "_10K RFU(mL-1)_")    
    2. Indicate number of timepoint(s) in the time course experiment.  
    3. Type in _name_ of a timepoint (e.g. 0h, 24h, 48h). This will be used to label dataframe later.  
    4. Upload your _*_Image.csv_ file from CellProfiler pipeline for each time point.   
    5. Type in directory path to save raw or normalized .csv files. (e.g. _/Users/a/Desktop/data/_)  
    """)
    #Define keys to keep track on timepoints and files uploaded
    t = 't_'
    u = 'upload_'

    #Read and parse tumor area raw data into individual DataGroup objects 
    for i in range(0,int(datapoint_input)) :
        time_point = st.text_input('Timepoint of dataset:', key= t + str(i))  
        uploaded_file = st.file_uploader("Select .csv file:", key= u + str(i)) 
        raw_data = pd.read_csv(uploaded_file)

        raw_TumorArea = raw_data['AreaOccupied_AreaOccupied_Identify_Tumor']
        file_name = raw_data['FileName_Orig_Tumor']
        dataObj = DataSeries(group_name, time_point, raw_TumorArea)
        datapoint.append(dataObj)
        filenamelist.append(file_name)

    st.write('___  ')
    #Display raw data table. Calculate mean, SD, SEM of tumor area of each timepoint    
    avg_dataObj = []
    std_dataObj = []
    sem_dataObj = []
    group_id = []
    n_row = []

    raw_df = pd.DataFrame(data= None)

    for i in range(0, int(datapoint_input)) :
        avg_dataObj.append(datapoint[i].calculateAvg(raw_TumorArea))
        std_dataObj.append(datapoint[i].calculateSD(raw_TumorArea))
        sem_dataObj.append(datapoint[i].calculateSEM(raw_TumorArea))   
        group_id.append(datapoint[i].name + '_' + datapoint[i].timepoint)
        n_row.append(datapoint[i].df.size)
        raw_df.insert(loc=i, column= group_id[i], value= datapoint[i].df) #Construct raw tumor area dataframe 
        tabulated_df = raw_df.join(filenamelist[i]) #Join filenames to its corresponnding data

    st.write("""### __Raw Data__ """)
    st.write(tabulated_df)
    st.write("""### __Mean, SD, SEM__ """)

    #Tabulate mean, SD, SEM of all datapoints into new dataframe
    df_summary = pd.DataFrame(data = [avg_dataObj, std_dataObj, sem_dataObj, n_row], index = ['Mean','SD','SEM', 'N'], columns= group_id)
    st.write(df_summary)

    with st.form('save_raw pixel_files') :
            save_dir = st.text_input('Type directory to save raw dataframe and Mean/SD/SEM .csv files:')
            tabulated_df_csv = os.path.join(save_dir, group_name + '_raw_dataframe.csv')
            raw_summary_csv = os.path.join(save_dir, group_name + '_raw_summary.csv')
            saved = st.form_submit_button('Save')
            if saved:
                tabulated_df.to_csv(tabulated_df_csv)
                df_summary.to_csv(raw_summary_csv)
                st.write('_Files saved_')


    st.write('___  ')

    #Normalize raw data to T-0h
    normalized_df = pd.DataFrame(data=None)
    avg_percent_change = []
    normalized_std = []
    normalized_sem = []
    normalized_n_row = []

    for i in range(0, int(datapoint_input)) :
        normalized_df.insert(loc= i, column= group_id[i], value= raw_df[group_id[i]]/raw_df[group_id[0]])
        tabulated_normalized_df = normalized_df.join(filenamelist[i])
        normalized_n_row.append(normalized_df[group_id[i]].size)
        avg_percent_change.append(normalized_df[group_id[i]].mean())
        normalized_std.append(normalized_df[group_id[i]].std())
        normalized_sem.append(normalized_df[group_id[i]].sem())


    st.write("""### __Normalized Data__ """)
    st.write(tabulated_normalized_df)
    st.write("""### __%Change, SD, SEM__ """)

    normalized_summary = pd.DataFrame(data = [avg_percent_change, normalized_std, normalized_sem, normalized_n_row], index = ['%Change','SD','SEM', 'N'], columns= group_id)
    st.write(normalized_summary)

    with st.form('save_normalized_files') :
        save_dir = st.text_input('Type directory to save normalized dataframe and %Change/SD/SEM .csv files:')
        tabulated_normalized_df_csv = os.path.join(save_dir, group_name + '_normalized_dataframe.csv')
        normalized_summary_csv = os.path.join(save_dir, group_name + '_normalized_summary.csv')
        saved = st.form_submit_button('Save')
        if saved:
            tabulated_normalized_df.to_csv(tabulated_normalized_df_csv)
            normalized_summary.to_csv(normalized_summary_csv)
            st.write('_Files saved_')


#Run statistical analysis and plot data
def PlotData() :

    condition_key = 'condition_'
    file_key = 'file_key_'

    name_list = []
    data_list = []
    sd_list = []
    sem_err_list = []

    st.header('Plot Data')
    st.write("""__Instructions:__   
    1. Name your condition as how you want it to display on the plot (e.g. Drug "A" - 1 mg/mL).  
    2. Upload your __<condition>_normalized_summary.csv__ files from Analyze Data mode.   
    3. Use sidebar options to customize your plot.  
    """)
    st.write('___  ')
    plot_title = st.sidebar.text_input('Type in plot title:')
    x_axis_input = st.sidebar.text_input('Type in timepoint(s), separated by a comma (e.g. "T-0h, T-24h"):')
    
    
    
    x_axis = x_axis_input.split(', ')

    st.write("""## _Plot Setup_  """)

    n_condition = st.text_input('Number of condition(s) to plot:')
    for i in range(0, int(n_condition)) : 
        condition_name = st.text_input("Name of condition:", key= condition_key + str(i))
        condition_file = st.file_uploader('Select file to upload', key= file_key + str(i))
        condition_data = pd.read_csv(condition_file, header=0, index_col=0)

        per_change = condition_data.iloc[0]
        sd = condition_data.iloc[1]
        sem = condition_data.iloc[2]
        plot_data_series = pd.Series(data= per_change)
        plot_sd_series = pd.Series(data= sd)
        plot_sem_series = pd.Series(data= sem)
        
        name_list.append(condition_name)
        data_list.append(plot_data_series)
        sd_list.append(plot_sd_series)
        sem_err_list.append(plot_sem_series)
    
    st.write('___  ')
    st.write("""## _Auto-Generated Plot_  """)

    fig = plt.figure(figsize= [6.0, 4.0])
    for i in range(0, int(n_condition)) :
        plt.errorbar(x= x_axis, y= data_list[i], yerr= sem_err_list[i], label= name_list[i], marker = 'o', capsize= 3)
    
    #Select plot theme
    theme_options = ['default', 'seaborn', 'ggplot', 'seaborn-white', 'seaborn-deep', 'grayscale']
    theme_selection = st.sidebar.selectbox('Select plot theme:', theme_options, index= 0)
    plt.style.use(theme_selection)

    #Scale y-axis 
    y_axis_lim = st.sidebar.slider('Select y-axis limit:',min_value= 0, max_value= 10, value= (0, 4))
    plt.ylim(y_axis_lim)

    #Label plot
    plt.title(plot_title)
    plt.grid(color = 'black', linestyle = 'dotted', linewidth = 0.2)
    plt.xlabel('Time point')
    plt.ylabel('% Change')
    plt.legend(loc= 'best')

    st.write(fig)
    st.write('_Error bars = SEM_  ')

#Main function 

modeOptions = ['Read Me', 'Extract Data', 'Analyze Data', 'Plot Data']

st.image(image='/Users/ducphan/Desktop/Streamlit/Linear_Logo.tif')
st.write('  ')
st.title('TUMOR GROWTH ANALYSIS')
st.write("This app will extract tumor area measurements from CellProfiler .csv files and perform tumor growth analysis.  ")

st.header('Select Mode:')
mode = st.radio("", modeOptions, index=0)
tabMethods = [ReadMe, ExtractData, AnalyzeData, PlotData]
tabMethods[modeOptions.index(mode)]()    