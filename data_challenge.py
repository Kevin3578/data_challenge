import pandas as pd
import matplotlib.pyplot as plt


fig, axs = plt.subplots(2, 3, figsize=(15, 10))

def convert_to_megabytes(size):
    if pd.isna(size) or size == 'VARIES WITH DEVICE':
        return None

    size = size.replace(',', '')
    if 'K' in size:      
      return float(size.replace('K', '')) / 1024
    elif 'M' in size:
      return float(size.replace('M', ''))
    elif 'G' in size:
        return float(size.replace('G', '')) * 1024
    else:
        return size


#file path locations
iosdata = './appleAppData.csv'
androiddata = './Google-Playstore.csv'

ios = pd.read_csv(iosdata)
android = pd.read_csv(androiddata)

#dictionary of categories for ios and android
iosvalues = {'games':['Games'], 'music':['Music'], 'health':['Health & Fitness']}
androidvalues = {'games': ['Action', 'Adventure', 'Arcade', 'Board', 'Card', 'Casino', 'Casual', 'Educational', 'Music', 'Puzzle', 
                 'Racing', 'Role Playing', 'Simulation', 'Sports', 'Strategy', 'Trivia', 'Word'], 'music': ['Music & Audio'], 'health': ['Health & Fitness']}


all_ios = [item for sublist in iosvalues.values() for item in sublist]
all_android = [item for sublist in androidvalues.values() for item in sublist]

#filtering data so only categories in dictionary are included
ios = ios.query('Primary_Genre in @all_ios')
ios = ios.rename(columns={'App_Name': 'App Name'})

android = android.query('Category in @all_android')

#converting size to megabytes
ios['Size'] = ios['Size_Bytes'] / (1024 * 1024)
ios = ios.drop(['Size_Bytes'], axis=1)

android['Size'] = android['Size'].str.upper()
android['Size'] = android['Size'].apply(convert_to_megabytes)


ios['Released'] = pd.to_datetime(ios['Released'])
android['Released'] = pd.to_datetime(android['Released'])

#splitting up by category
android_games = android.query('Category in @androidvalues["games"]')
android_music = android.query('Category in @androidvalues["music"]')
android_health = android.query('Category in @androidvalues["health"]')

ios_games = ios.query('Primary_Genre in @iosvalues["games"]')
ios_music = ios.query('Primary_Genre in @iosvalues["music"]')
ios_health = ios.query('Primary_Genre in @iosvalues["health"]')

#combining android and ios for app sizes
games_sizes = pd.concat([android_games['Size'], ios_games['Size']]).reset_index(drop=True)
music_sizes = pd.concat([android_music['Size'], ios_music['Size']]).reset_index(drop=True)
health_sizes = pd.concat([android_health['Size'], ios_health['Size']]).reset_index(drop=True)

games_monthly_counts = pd.concat([android_games[['Released', 'Size', 'App Name']], ios_games[['Released', 'Size', 'App Name']]], axis=0)
music_monthly_counts = pd.concat([android_music[['Released', 'Size', 'App Name']], ios_music[['Released', 'Size', 'App Name']]], axis=0)
health_monthly_counts = pd.concat([android_health[['Released', 'Size', 'App Name']], ios_health[['Released', 'Size', 'App Name']]], axis=0)

#grouping number of apps released by month
games_monthly_counts['Released'] = pd.to_datetime(games_monthly_counts['Released'], utc=True)
games_monthly_counts['year_month'] = games_monthly_counts['Released'].dt.to_period('M')
games_year_month = games_monthly_counts.groupby('year_month').size()
games_year_month.plot(kind='line',ax=axs[1,0])
axs[1,0].set_title('Games released per month')
axs[1,0].set_xlabel('Month')
axs[1,0].set_ylabel('Number of apps released')

music_monthly_counts['Released'] = pd.to_datetime(music_monthly_counts['Released'], utc=True)
music_monthly_counts['year_month'] = music_monthly_counts['Released'].dt.to_period('M')
music_year_month = music_monthly_counts.groupby('year_month').size()
music_year_month.plot(kind='line',ax=axs[1,1])
axs[1,1].set_title('Music apps released per month')
axs[1,1].set_xlabel('Month')
axs[1,1].set_ylabel('Number of apps released')

health_monthly_counts['Released'] = pd.to_datetime(health_monthly_counts['Released'], utc=True)
health_monthly_counts['year_month'] = health_monthly_counts['Released'].dt.to_period('M')
health_year_month = health_monthly_counts.groupby('year_month').size()
health_year_month.plot(kind='line',ax=axs[1,2])
axs[1,2].set_title('Health & fitness apps released per month')
axs[1,2].set_xlabel('Month')
axs[1,2].set_ylabel('Number of apps released')

#counting largest 10 apps by size per year
games_monthly_counts['year'] = games_monthly_counts['Released'].dt.year
top_games_per_year = games_monthly_counts.groupby('year').apply(lambda x: x.nlargest(10, 'Size')).reset_index(drop=True)

music_monthly_counts['year'] = music_monthly_counts['Released'].dt.year
top_music_per_year = music_monthly_counts.groupby('year').apply(lambda x: x.nlargest(10, 'Size')).reset_index(drop=True)

health_monthly_counts['year'] = health_monthly_counts['Released'].dt.year
top_health_per_year = health_monthly_counts.groupby('year').apply(lambda x: x.nlargest(10, 'Size')).reset_index(drop=True)

pd.set_option('display.max_rows', None)
print('Largest games by app size in MB per year')
print(top_games_per_year[['App Name', 'Size', 'year']])

print('Largest music apps by app size in MB per year')
print(top_music_per_year[['App Name', 'Size', 'year']])

print('Largest health & fitness apps by app size in MB per year')
print(top_health_per_year[['App Name', 'Size', 'year']])


# Filter out any data outside these percentile limits
lower_games = games_sizes.quantile(0.01)
upper_games = games_sizes.quantile(0.99)

games_sizes = games_sizes[(games_sizes > lower_games) & (games_sizes < upper_games)]

axs[0,0].hist(games_sizes, bins=50, edgecolor='black')
axs[0,0].set_xlabel('Size in MB')
axs[0,0].set_ylabel('Frequency')
axs[0,0].set_title('Distribution of app sizes for Games')

lower_music = music_sizes.quantile(0.01)
upper_music = music_sizes.quantile(0.99)

music_sizes = music_sizes[(music_sizes > lower_music) & (music_sizes < upper_music)]

axs[0,1].hist(music_sizes, bins=50, edgecolor='black')
axs[0,1].set_xlabel('Size in MB')
axs[0,1].set_ylabel('Frequency')
axs[0,1].set_title('Distribution of app sizes for Music')

lower_health = health_sizes.quantile(0.01)
upper_health = health_sizes.quantile(0.99)

health_sizes = health_sizes[(health_sizes > lower_health) & (health_sizes < upper_health)]

axs[0,2].hist(health_sizes, bins=50, edgecolor='black')
axs[0,2].set_xlabel('Size in MB')
axs[0,2].set_ylabel('Frequency')
axs[0,2].set_title('Distribution of app sizes for health and fitness')

plt.show()


#calculating average rating for each app category
android_games_total_rating  = (android_games['Rating'] * android_games['Rating Count']).sum()
android_games_total_rating_count = android_games['Rating Count'].sum()
ios_games_total_rating = (ios_games['Average_User_Rating'] * ios_games['Reviews']).sum()
ios_games_total_rating_count = ios_games['Reviews'].sum()
games_average = (android_games_total_rating + ios_games_total_rating) / (android_games_total_rating_count + ios_games_total_rating_count)

android_music_total_rating  = (android_music['Rating'] * android_music['Rating Count']).sum()
android_music_total_rating_count = android_music['Rating Count'].sum()
ios_music_total_rating = (ios_music['Average_User_Rating'] * ios_music['Reviews']).sum()
ios_music_total_rating_count = ios_music['Reviews'].sum()
music_average = (android_music_total_rating + ios_music_total_rating) / (android_music_total_rating_count + ios_music_total_rating_count)

android_health_total_rating  = (android_health['Rating'] * android_health['Rating Count']).sum()
android_health_total_rating_count = android_health['Rating Count'].sum()
ios_health_total_rating = (ios_health['Average_User_Rating'] * ios_health['Reviews']).sum()
ios_health_total_rating_count = ios_health['Reviews'].sum()
health_average = (android_health_total_rating + ios_health_total_rating) / (android_health_total_rating_count + ios_health_total_rating_count)

#round to 2 decimal places
games_average = round(games_average, 2)
music_average = round(music_average, 2)
health_average = round(health_average, 2)
print('average rating of games apps: ' + str(games_average))
print('average rating of music apps: ' + str(music_average))
print('average rating of health and fitness apps: ' + str(health_average))
