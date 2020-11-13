# Habit Tracker Specification
 ## The web app should suport the following features:

 ### User
- The user should be able to login and logout 
- A user that is not logged in should be presented with the following options in the navbar: 
    - Login/create account
- When logged in the user should have the following options available to them in the navbar:
    - Sign out
    - Profile
    - Habits
- When the user is logged in they should be able to click their username to link their profile. If they are not logged in then an attempt to view should bring them to the loggin page.

 ### Profile 
 User profile
- A user:
   - should have the options be able to create a new habit
   - can remove/delete habits
   - can view the habits of others that that have added them
   - can accept or reject habit-view reuests
   - can view new activity 
- They are presented with a list of their habits
   - They can click on a habit to view data on it
   - They can delete a habit and all its data

### Habit
A habit is a category that a user creates to add data to
- A habit page should show:
   - the name of the habit
   - if the user is not the owner, they should see the owner name
   - overall activity for the current week (sat - sun)
   - The owner should have the option to add a data point to the habit
- The graph
   - It should show data points for each day and empty if there is no data
   - Hovering over a point will display summary data
      - This includes: timelabel (day, month or year), value total 
   - If data is missing between two points, the graph should interpolate linearly
   - There should be an option to view points by day, week, month, year, 5 year, or overall
   - switching between goes to the corresponding level up in time scales. Going to a more fine time scale starts in january.
   - There is an option to view the next time step if one exists with data. 
- If the user is not the owner or on the view list then they should be presented with an error that redirects them to their profile page when they try to access that habit.
- When an entry is clicked they should be redirected to a entry page.
- All sub habits should be listed and graphs can be displayed showing component by sub habit 
- There should be an option to add a subhabit to a graph
- All future data points will have sub habit divisions but not previous data points
- If the user if the owner then they will have the option to send view requests and remove people from the view
- If the user is on the view list but not the owner then they will have the option to not view that habit

### Subhabit
A subhabit is a subdivision of a main habit. 
- When clicking on a subhabit it presents a page that is similar to the habit page
- A sub habit should have the option to add a entry and edit entries as before
- Subhabit entries should be able to swtich from habit to habit  

### AcivityLog
Has log on updates of habit
- When a habit is updated, it updates the activity log on the viewing users
- If email is activated then send email?
- When a viewer view notification, it is removed from the log or 

### Entry  
These represent the data points in habit
- The entry page should have all data displayed: timelabel (day, month or year), value avg, value total, and notes
- If there are sub habits then they should be listed with their data under
- If the user is the owner, they will have the option to edit the habit entry
- If there is a sub habit then they will add the entry to the sub habit category or 'other' option.  
