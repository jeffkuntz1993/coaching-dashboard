import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Coaching Questionnaire Dashboard", layout="wide")
st.title("🏆 Qualities of Coaching Survey Dashboard")
st.markdown("Filter the survey responses on the left and see how different groups answered the questions.")

@st.cache_data
def load_data():
    df = pd.read_csv('Qualities of Coaching Questionnaire (Current Responses) - Form Responses 1.csv')
    
    rename_mapping = {
        'What is your current age?': 'Age',
        'For which teams do you participate at Santa Fe?': 'Team Type',
        'Do you more love to win or hate to lose?': 'Win vs Lose Preference',
        'Would you prefer to be on a winning team but yourself mostly sit the bench, or play an equal share as your teammates on a team that rarely wins? ': 'Play vs Bench Preference',
        'How do you prefer to be coached?': 'Coaching Preference'
    }
    df.rename(columns=rename_mapping, inplace=True)
    return df

df = load_data()

# -------------------------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------------------------
st.sidebar.header("🔍 Filter Responses")

age_options = df['Age'].dropna().unique()
team_options = df['Team Type'].dropna().unique()
win_lose_options = df['Win vs Lose Preference'].dropna().unique()
play_bench_options = df['Play vs Bench Preference'].dropna().unique()
coaching_pref_options = df['Coaching Preference'].dropna().unique()

selected_age = st.sidebar.multiselect("Select Age Group(s)", options=age_options, default=age_options)
selected_team = st.sidebar.multiselect("Select Team Type(s)", options=team_options, default=team_options)
selected_win_lose = st.sidebar.multiselect("Love to Win or Hate to Lose?", options=win_lose_options, default=win_lose_options)
selected_play_bench = st.sidebar.multiselect("Play vs Bench Preference", options=play_bench_options, default=play_bench_options)
selected_coaching = st.sidebar.multiselect("Coaching Preference", options=coaching_pref_options, default=coaching_pref_options)

filtered_df = df[
    (df['Age'].isin(selected_age)) &
    (df['Team Type'].isin(selected_team)) &
    (df['Win vs Lose Preference'].isin(selected_win_lose)) &
    (df['Play vs Bench Preference'].isin(selected_play_bench)) &
    (df['Coaching Preference'].isin(selected_coaching))
]

st.sidebar.markdown(f"**Current active responses:** {len(filtered_df)} out of {len(df)}")

# -------------------------------------------------------------------------
# VISUALIZATIONS
# -------------------------------------------------------------------------

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your criteria.")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("How do athletes prefer to be coached?")
        pref_counts = filtered_df['Coaching Preference'].value_counts().reset_index()
        pref_counts.columns = ['Coaching Preference', 'Count']
        
        fig1 = px.pie(pref_counts, names='Coaching Preference', values='Count', hole=0.4, 
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Play equal share (losing team) vs. Sit bench (winning team)")
        play_counts = filtered_df['Play vs Bench Preference'].value_counts().reset_index()
        play_counts.columns = ['Preference', 'Count']
        
        fig2 = px.bar(play_counts, x='Preference', y='Count', color='Preference',
                      text='Count', color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="Number of Athletes")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Define color maps for ranking (Green for 1st, Red for last)
    rank_5_colors = {"1.0": "#2ca02c", "2.0": "#98df8a", "3.0": "#ffffbf", "4.0": "#ff9896", "5.0": "#d62728"}
    rank_4_colors = {"1.0": "#2ca02c", "2.0": "#98df8a", "3.0": "#ff9896", "4.0": "#d62728"}

    col3, col4 = st.columns(2)

    # Visual 3: Reasons for Playing (Stacked Bar)
    with col3:
        st.subheader("Top Reasons for Playing")
        st.markdown("*Hover to see how many athletes gave each rank. Green = Ranked 1st, Red = Ranked 5th.*")
        
        reason_cols = [col for col in df.columns if 'Read all five factors below' in col]
        if reason_cols and not filtered_df[reason_cols].dropna(how='all').empty:
            # Sort factors by best average rank (lowest number = best)
            avg_ranks = filtered_df[reason_cols].mean().sort_values(ascending=True)
            sorted_reasons = [x.split('[')[-1].replace(']', '') for x in avg_ranks.index]
            
            # Melt data for stacked charting
            melted_reasons = filtered_df[reason_cols].melt(var_name='Reason', value_name='Rank').dropna()
            melted_reasons['Reason'] = melted_reasons['Reason'].apply(lambda x: x.split('[')[-1].replace(']', ''))
            melted_reasons['Rank'] = melted_reasons['Rank'].astype(float).astype(str)
            
            rank_counts = melted_reasons.groupby(['Reason', 'Rank']).size().reset_index(name='Count')
            
            fig3 = px.bar(rank_counts, y='Reason', x='Count', color='Rank', orientation='h',
                          category_orders={"Reason": sorted_reasons, "Rank": ["1.0", "2.0", "3.0", "4.0", "5.0"]},
                          color_discrete_map=rank_5_colors)
            
            # Add autorange="reversed" so the first item in our list appears at the very top
            fig3.update_layout(xaxis_title="Number of Votes", yaxis_title="", barmode='stack', legend_title="Rank",
                               yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig3, use_container_width=True)

    # Visual 4: Ideal Coach Qualities (Stacked Bar)
    with col4:
        st.subheader("Importance of Coach Qualities")
        st.markdown("*Hover to see how many athletes gave each rank. Green = Ranked 1st, Red = Ranked 4th.*")
        
        coach_cols = [col for col in df.columns if 'Once you have read the definitions above' in col]
        if coach_cols and not filtered_df[coach_cols].dropna(how='all').empty:
            # Sort factors by best average rank (lowest number = best)
            avg_ranks_coach = filtered_df[coach_cols].mean().sort_values(ascending=True)
            sorted_coach = [x.split('[')[-1].replace(']', '') for x in avg_ranks_coach.index]
            
            # Melt data
            melted_coach = filtered_df[coach_cols].melt(var_name='Quality', value_name='Rank').dropna()
            melted_coach['Quality'] = melted_coach['Quality'].apply(lambda x: x.split('[')[-1].replace(']', ''))
            melted_coach['Rank'] = melted_coach['Rank'].astype(float).astype(str)
            
            rank_counts_coach = melted_coach.groupby(['Quality', 'Rank']).size().reset_index(name='Count')
            
            fig4 = px.bar(rank_counts_coach, y='Quality', x='Count', color='Rank', orientation='h',
                          category_orders={"Quality": sorted_coach, "Rank": ["1.0", "2.0", "3.0", "4.0"]},
                          color_discrete_map=rank_4_colors)
            
            # Add autorange="reversed" so the first item in our list appears at the very top
            fig4.update_layout(xaxis_title="Number of Votes", yaxis_title="", barmode='stack', legend_title="Rank",
                               yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig4, use_container_width=True)

    # Allow users to explore raw answers to free-text questions
    st.divider()
    st.subheader("📝 Open-Ended Feedback")
    
    negative_qualities_col = "Think about coaches you've had. What negative qualities did they possess?"
    positive_qualities_col = "Think of the BEST coach you've had. What qualities does he/she possess?"
    
    tab1, tab2 = st.tabs(["Negative Qualities Experienced", "Best Coach Qualities"])
    
    with tab1:
        for idx, response in enumerate(filtered_df[negative_qualities_col].dropna()):
            st.info(f'"{response}"')

    with tab2:
        for idx, response in enumerate(filtered_df[positive_qualities_col].dropna()):
            st.success(f'"{response}"')

# Display raw data table option at the bottom
if st.checkbox("Show Raw Data Table"):
    st.dataframe(filtered_df)
