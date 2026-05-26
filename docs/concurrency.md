# Concurrency Test Cases

Without Conurrency Control, we would run into the following problems:

1: Drty Read for our create functions 
When going through our create implementations, if we had no concurrency control, we would end up with a Dirty Read becuase we would then have set it up to where we create somehting and then give it other info within the same function without commited, creating this Dirty Read phenomnia. What we do instead is we isolated by doing a READ COMMIT isolation where what we create and then commit it before we added any other info. We do this by spereating out our create functions form anyother functions so that we never run into this issue.

DIGRAM 
CREATE
USER--->ENTERS Email in create page ----> Send request to Server ----> Checks create in the DataBase ---> Create is vail sent back to server
--> Create user is succeful in server ---> send success message to user

2: phantom read for our logs and plan
Our logs and plan have similar attributes that make it tempting to put them togehter in the same functions. This would be the case if we had no concurrency control, however we would end up with the phantom read phenomina if we did this. Logs and plans have inserset and delete function in them and pull from the same data. With this, there a bunch of data being pull out or insterset or even delete. If we have these functions together, there could be much coflicted in rows being changes and trying to pull A but because one pull it earlier, it pull B instead. In order to prevent this, we isolated by doing a SERIALIZABLE isolation where we completly seprated the data by putting the function in two sepreate files so we can garrently they do not run at the same time and they pull form the same database on their terms so whatever they change is just form there own shake, not impacting each other. Thus, all tranaction never happen at the same time

DIGRAM
Logs
USER--->ENTERS LOG info ----> Send request to Server ----> Pull info from the DataBase ---> Data is found is sent to server ---> server sends that data and inserts date into to the Log data base
--> Log info is succeful inputed to server ---> send success message to user

HAPPENS ON A DIFFERNT CALL
PLAN
USER--->ENTERS Plan info ----> Send request to Server ----> Pull info from the DataBase ---> Data is found is sent to server ---> server sends that data and inserts date into to the Plan data base
--> Plan info is succeful inputed to server ---> send success message to user


3: Phantom read for our add functions

For our add function, we have to be careful of Phantom Read since multiply itmes can be added at the same item. Without conurrency control, we could try to added a ton of items in the same function and cause the possible of missing items or instering items in wrong order or some other bad thing. They way we isolated this is by doing a SERIALIZABLE isolation where in every tranaction in an add function, there is one for every item. We use for loops to do this, one inserting one item at the time and since we will never be entering a massive amount of items per person, this should not slow down preformace.


DIGRAM
ADD
USER--->ENTERS info to be ADD ----> Send request to Server ----> ADD one row of info to the DataBase (REPATES this speate N time) ---->  data base
--> info is succeful inputed database and server ---> send success message to user





