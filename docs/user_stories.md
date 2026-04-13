# User Stories:
1. As an user wanting to track my health, I want to log my meal with specific carb, protein, and fat values so that I can have an accurate record of my nutrition intake.
2. As an user trying to fix my meal routine, I want to track the time I eat my meals so that I can prevent eating late.
3. As an user who's trying to balance nutrition throughout the day, I want to filter my meal based on my nutrition density so that I can ensure I get uniform nutrition throughout the day.
4. As a gym rat trying to build muscle, I want to log my protein intake and find meals with the highest count of protein so that I can build muscle more efficiently.
5. As an user who like organizing everything, I want to keep track of my meals and categorize them based on nutrients and times of day so that I can have my diet in an organized space.
6. As a user with dietary restrictions, I want to set my restrictions and log meals and view warnings for restricted nutrients or ingredients, so that I can avoid unsafe foods. 
7. As a user who takes supplements, I want to log vitamins and supplements and view how they contribute to my daily nutrient totals, so that I can avoid deficiencies or overdoses.
8. As a budget-conscious user, I want to input the cost of foods I eat and view the nutritional value per dollar, so that I can eat healthily on a budget.
9. As an athlete, I want to identify the needed macromolecule intake for my weight and height so that I can build my nutrition around bulking or cutting.
10. As the family grocery-shopper, I want to easily store and access a list of all of our favorite meals and their needed ingredients, so that I can keep myself organized while I shop.
11. As a person with a sweet tooth, I want to view warnings that display high-sugar content for a meal I am planning, so that I can avoid exceeding my personal sugar limit.
12. As a researcher , I want to be able to study how different foods that I eat affect me and be able to provide the public acturate information on different foods and how they affect us
13. As a parent, I want to make sure I am giving my childern a good healthy deit that will build up their bodies
14. As a coach, I want to have an easy way to see how certian diets have their affect so I can give the best advice  on what my team should eat so it will improve them as they growth in their sport

# Exceptions: 
1. A user enters a negative value for any nutrient; system would reject the entry and ask a positive number.
2. A user enters a future date for logging in their meal; system would reject the entry and default to current timestamp.
3. A user enters incomplete meal data; the system would show an error about incomplete fields, and not allow them to save data until corrected.
4. A user sets an unrealistic nutrition goal (e.g., extreme calorie deficit); the system warns the user and suggests a safer recommended range.
5. A user uploads a custom food with extremely large data (e.g., too many ingredients); the system rejects the entry and enforces size limits.
6. A user enters invalid values for their height and/or weight (ex: negative numbers or text); the system will not allow the value to be entered and return an error message.
7. A user catalogs a meal that has the exact name of another non-identical meal; the system will display a warning and prevent the meal from being entered without a name change.
8. A user attempts to search for or edit a meal that does not exist; the system will prevent the change or search from occuring and return an error message.
9. A user attempts to put down the same meal twice for the same day; the system will provide a warning telling the user they might have accidentally put the same meal twice
10. A user attempts to put down abnormal heights and weight for their age; the system will provide a warning telling the user they double check their height and weight before going forth
11. A user attempts to put down a negative value for age; the system will reject this and ask for a positive age number
12. A user attempts to put down a number for their names; they system will reject and ask for a alphabetical name 
