
"""
Copyright (c) 2023 Rajat Chandak, Shubham Saboo, Vibhav Deo, Chinmay Nayak
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/VibhavDeo/FitnessApp

"""

""""Importing app from apps.py"""
from .apps import App
import json

app = App()
mongo = app.mongo


def insertfooddata():
    """Inserting the food data from CSV file to MongoDB"""
    # with open("food_data/calories.csv", "r", encoding="ISO-8859-1") as file:
    f = open("food_data/calories.csv", "r", encoding="ISO-8859-1")
    l = f.readlines()

    for i in range(1, len(l)):
        l[i] = l[i][1:len(l[i]) - 2]

    for i in range(1, len(l)):
        temp = l[i].split(",")
        mongo.db.food.update_one(
            {'food': temp[0]}, {'$set': {'calories': temp[1]}}, upsert=True)


def insertexercisedata():
    """Define exercise data for all 9 exercises"""
    exercise_data = [
        {
            "email": "email",
            "exercise_id": 1,
            "image": "../static/img/yoga.jpg",
            "video_link": "https://www.youtube.com/watch?v=c8hjhRqIwHE",
            "name": "Yoga for Beginners",
            "intro": "New to Yoga? You are at the right place! Learn easy yoga poses to build strength, flexibility, and mental clarity.",
            "description": "<br>Join Anvita &amp; Tejashree for this 30 minute Gentle Yoga session, which has an emphasis on asana alignments, breathing techniques and mindfulness. This class will focus on the Core and abdominal region to help build strength in the midsection of the body and the lower back. Through the asanas in this class, you will build endurance, stamina, and overall agility.<br><br><strong>Main Practice:</strong><br><br>1. Vayunishkasana<br>2. Surya Namaskar - 3 Rounds<br>3. Ardha Uttanasana + Ardha Utkatasana<br>4. Anjaneyasana Lateral Stretch<br>5. Eka Pada Adho Mukha - Knee to Elbow<br>6. Parivrtta Janu Shrishasana<br>7. Supta Dandasana + Pada Sanchalanasana<br><br><br>",
            "plan_image": "../static/img/yoga_stages.png",
            "href": "yoga"
        },
        {
            "email": "email",
            "exercise_id": 2,
            "image": "../static/img/swim.jpeg",
            "video_link": "https://www.youtube.com/watch?v=oM4sHl1hTEE",
            "name": "Swimming",
            "intro": "Swimming is an activity that burns lots of calories, is easy on the joints, supports your weight, builds muscular strength and endurance.",
            "description": "<br>There are plenty of reasons to swim! Here's a list that should get you motivated. <br> <strong><b>Low impact</b></strong><br>There's no ground impact when you swim, and so you protect the joints from stress and strain. Water aerobics classes are also desirable for this reason because even if you do jump and hit the bottom of the pool,  you do so with less force because you're buoyant in the water.<br><br> <strong><b>Can be continued for a lifetime</b></strong><br>Because there's no impact on swimming, it can be continued for a lifetime.Because there's no impact on swimming, it can be continued for a lifetime.Because there's no impact on swimming, it can be continued for a lifetime.<br><br> <strong><b>Builds muscle mass</b></strong><br>In a study of men who completed an eight-week swimming program, there was a 23.8% increase in the triceps muscle (the back of the arm).<br><br> <strong><b>Builds cardiorespiratory fitness</b></strong><br>Swimming improves endurance. In one study of sedentary middle-aged men and women who did swim training for 12 weeks, maximal oxygen consumption improved 10% and stroke volume (the amount of blood pumped with each beat which indicates heart strength) improved as much as 18%.",
            "plan_image": "../static/img/swim.jpeg", #TODO: find an image for swimming program plan
            "href": "swim"
        },
        {
            "email": "email",
            "exercise_id": 3,
            "image": "../static/img/R31.jpg",
            "video_link": "https://www.youtube.com/watch?v=z6GxFSsx84E",
            "name": "Abs Smash",
            "intro": "Whether your goal is a six-pack or just a little more definition around your midsection, we will help get you there!",
            "description": "<br>Bolt on these targeted abs workouts to your main session to sculpt a rock-hard six-pack. If you’re looking to train your abs, the good news is that there are a huge variety of exercises that will help you achieve that goal. <br><br><strong>Main Practice:</strong><br><br>1. Plank<br>2. Single-leg Romanian deadlift <br>3. Squats<br>4. Overhead presses <br>5. Deadlifts <br>6. Push ups<br>7. Pull ups <br><br><br>",
            "plan_image": "../static/img/abs_smash.jpeg",
            "href": "abs_smash"
        },
        {
            "email": "email",
            "exercise_id": 4,
            "image": "../static/img/walk.jpg",
            "video_link": "https://www.youtube.com/watch?v=3hlUMzWh8jY",
            "name": "Walk Fitness",
            "intro": "Join us to get the best of the walk workouts to burn more calories than a stroll around the park.",
            "description": "<br><strong><b>Walking can be as good as a workout, if not better, than running</b></strong> <br>walking is a really good form of exercise and can help you reach your fitness and weight-loss goals.\
                            <br>Explore your environment on foot. Notice what is going on around you and you'll find you never really walk the same way twice. There are always new things to see.\
                            <br><br>Find pleasant places to walk. Look for walking paths, greenways, and pedestrian streets to enjoy.\
                            <br>Bring along your family and friends. Walking together is a great way to connect with others.\
                            <br>Walk instead of drive for a few trips each week. Walk part of your commute to work or school. Leave the car behind or get off a stop early on public transit. Walk to the store for small items. You'll save money and have a purpose for getting in your daily steps.\
                            <br>Try a charity walk to raise money for a cause. Put your steps to good use.<br><br><br><br>",
            "plan_image": "../static/img/walk_group.jpeg",
            "href": "walk"
        },
        {
            "email": "email",
            "exercise_id": 5,
            "image": "../static/img/R21.jpg",
            "video_link": "https://www.youtube.com/watch?v=8MAtXXXUvqo",
            "name": "Belly Burner",
            "intro": "Join Sasha for a 30-minute no-equipment workout that will work on that stubborn belly fat.",
            "description": "<br> Who doesn't want to be able to slip into a pair of jeans without having to deal with a muffin top? Losing belly fat is a surefire way to improve your health. Join us for some great core-focused exercises that will torch fat all over the body, resulting in a strong and more chiseled core. <br><br><strong>Main Practice:</strong><br><br>1. Mountain Climbers<br>2. Burpees <br>3. Turkish Get-up <br>4. Medicine Ball Burpees <br>5. Sprawls <br>6. Side to Side Slams<br>7. Russian Twists <br><br><br>",
            "plan_image": "../static/img/belly.jpeg",
            "href": "belly"
        },
        {
            "email": "email",
            "exercise_id": 6,
            "image": "../static/img/R22.jpg",
            "video_link": "https://www.youtube.com/watch?v=Qf0L-xtMUjg",
            "name": "Dance Fitness",
            "intro": "Shake it off and groove to some fun tracks with Tom and his squad in this dance fitness session!",
            "description": "<br><strong><b>Simply put, dance cardio is utilizing different types of dance to exercise your body.</b></strong> <br>Build new muscle mass and strip away belly fat fast to reveal a lean, hard physique in 28 days\
                            <br> There are many types of dance cardio programs to choose from, so you can change your routine as often as you want to.\
                            <br><br><strong><b>1. Zumba Dancing</b></strong><br><strong><b>2. Bollywood dancing</b></strong><br><strong><b>3. Hula Hoop Dancing</b></strong><br><strong><b>4. Salsa</b></strong><br><br><br><br>",
            "plan_image": "../static/img/R22.jpg", #TODO: find an image for dance program plan
            "href": "dance"
        },
        {
            "email": "email",
            "exercise_id": 7,
            "image": "../static/img/R23.jpg",
            "video_link": "https://www.youtube.com/watch?v=Ze7zzMgCdko",
            "name": "HRX Fitness",
            "intro": "It's time to push yourself to the limit! Join us for some intense workout sessions.",
            "description": "<br><strong><b>Inspired by Hrithik Roshan’s fitness journey, the HRX Workout is based on a strength training module.</b></strong> <br> The HRX Workout primarily focuses on your shoulders, quads, core, traps and deltoid muscles.\
                            <br>It is designed keeping in mind all age groups and involves working on specific muscles using weights and various movements.\
                            <br><br>These include Primal Movements, Zero Momentum Reps and Compound Movements.\
                            <br>It also involves core activation and helps build body strength.\
                            <br>At HRX, it’s our mission to motivate and enable you to work on your mind and body, making sure you can be the best version of you.\
                            <br>Not just a brand, HRX is a mission that helps us enable and support people to be the fittest, happiest and most confident version of themselves.<br><br><br><br>",
            "plan_image": "../static/img/hrx.jpeg",
            "href": "hrx"
        },
        {
            "email": "email",
            "exercise_id": 8,
            "image": "../static/img/R32.jpg",
            "video_link": "https://www.youtube.com/watch?v=XH7mBWRG9q0",
            "name": "Core Conditioning",
            "intro": "Develop core muscle strength that improves posture and contributes to a trimmer appearance.",
            "description": "<br> Develop a strong core for more than the six-pack abs that will hopefully peak through. Use core conditioning to improve your overall athletic performance and life—the flat abs are just a bonus. <br><br><strong>Main Practice:</strong><br><br>1. Plank<br>2. Reverse Crunch <br>3. Bird Dog Crunch <br>4. Glute Bridge <br>5. Russian Twist <br>6. Towel Plank knee-inn<br>7. Bicycle crunch <br><br><br>",
            "plan_image": "../static/img/core.jpeg",
            "href": "core"
        },
        {
            "email": "email",
            "exercise_id": 9,
            "image": "../static/img/R11.jpg",
            "video_link": "https://www.youtube.com/watch?v=8IjCdiweJQo",
            "name": "Gym",
            "intro": "A collection of Dumbbells workouts by skilled trainers specific to a particular muscle group.",
            "description": "<br><strong><b>A Four-Week Gym Workout Routine To Get Big And Lean</b></strong> <br>Build new muscle mass and strip away belly fat fast to reveal a lean, hard physique in 28 days\
                            <br>All four weekly workouts are made up of five moves, which you’ll perform as straight sets, so you’ll simply work through moves 1 to 5 in order. That’s it!\
                            <br><br><strong><b>1. Chest And Triceps</b></strong><br><strong><b>2. Back And Biceps</b></strong><br><strong><b>3. Legs And Abs</b></strong><br><strong><b>4. Back And Shoulders</b></strong><br><br><br><br>",
            "plan_image": "../static/img/gym_group.jpeg",
            "href": "gym"
        }
    ]

    # Connect to MongoDB

    collection = mongo.db["your_exercise_collection"]

    # Insert exercise data into MongoDB
    for exercise in exercise_data:
        query = {"exercise_id": exercise["exercise_id"]}
        update = {"$set": exercise}
        collection.update_one(query, update, upsert=True)

def insert_program_plan_data():
    # Connect to MongoDB
    collection = mongo.db["program_plan"]

    with open("program_plan/program_plan.json") as f:
        program_plan_data = json.load(f)
    
    # Insert program plan data into MongoDB
    for program_plan in program_plan_data:
        query = {"title": program_plan["title"]}
        update = {"$set": program_plan}
        collection.update_one(query, update, upsert=True)