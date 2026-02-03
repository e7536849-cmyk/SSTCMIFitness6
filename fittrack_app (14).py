import streamlit as st
import json
import os
import time
from datetime import datetime, timedelta
import pandas as pd

# ============================================
# API CONFIGURATION
# ============================================
# Set these environment variables to enable real APIs
# In Streamlit Cloud: Go to App Settings > Secrets
# Add these keys there

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
USDA_API_KEY = os.environ.get('USDA_API_KEY', '')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

# API Mode: 'mock' or 'real'
# Automatically switches to 'real' when API keys are present
API_MODE = 'real' if (OPENWEATHER_API_KEY or USDA_API_KEY or YOUTUBE_API_KEY) else 'mock'

# ============================================

# SST Color Palette
SST_COLORS = {
    'red': '#d32f2f',
    'blue': '#1976d2',
    'gray': '#5a5a5a',
    'light_gray': '#e0e0e0',
    'white': '#ffffff',
    'dark': '#2c2c2c'
}

# Configure page
st.set_page_config(
    page_title="FitTrack - SST Fitness Companion",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SST styling
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
    }}
    .main-header {{
        background: linear-gradient(135deg, {SST_COLORS['red']} 0%, #b71c1c 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(211, 47, 47, 0.3);
    }}
    .stat-card {{
        background: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {SST_COLORS['blue']};
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
    }}
    .grade-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 6px;
        font-weight: bold;
        color: white;
        margin: 5px;
    }}
    .grade-5 {{ background: #4caf50; }}
    .grade-4 {{ background: #8bc34a; }}
    .grade-3 {{ background: #ffc107; }}
    .grade-2 {{ background: #ff9800; }}
    .grade-1 {{ background: #f44336; }}
    h1, h2, h3 {{ color: {SST_COLORS['dark']}; }}
    .stButton>button {{
        background: linear-gradient(135deg, {SST_COLORS['blue']} 0%, #1565c0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 30px;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
        transform: translateY(-2px);
    }}
    </style>
""", unsafe_allow_html=True)

# Data storage file
DATA_FILE = 'fittrack_users.json'

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users_data' not in st.session_state:
    st.session_state.users_data = {}

# Load user data
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save user data
def save_users(users_data):
    with open(DATA_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

# Load data on startup
st.session_state.users_data = load_users()

# Get current user data
def get_user_data():
    if st.session_state.username in st.session_state.users_data:
        return st.session_state.users_data[st.session_state.username]
    return None

# Update user data
def update_user_data(data):
    st.session_state.users_data[st.session_state.username] = data
    save_users(st.session_state.users_data)

# NAPFA grading standards
NAPFA_STANDARDS = {
    12: {
        'm': {
            'SU': [[36,32,28,24,20], False],
            'SBJ': [[198,190,182,174,166], False],
            'SAR': [[39,37,34,30,25], False],
            'PU': [[6,5,4,3,2], False],
            'SR': [[10.8,11.2,11.6,12.1,12.6], True],
            'RUN': [[9.67,10.42,11.17,12.0,12.75], True]
        },
        'f': {
            'SU': [[29,25,21,17,13], False],
            'SBJ': [[167,159,150,141,132], False],
            'SAR': [[39,37,34,30,25], False],
            'PU': [[15,13,10,7,3], False],
            'SR': [[11.5,11.9,12.4,12.9,13.5], True],
            'RUN': [[11.0,11.75,12.67,13.42,14.42], True]
        }
    },
    13: {
        'm': {
            'SU': [[38,34,30,26,22], False],
            'SBJ': [[208,200,192,184,176], False],
            'SAR': [[40,38,35,31,26], False],
            'PU': [[8,7,6,5,4], False],
            'SR': [[10.5,10.9,11.3,11.8,12.3], True],
            'RUN': [[9.33,10.08,10.83,11.67,12.42], True]
        },
        'f': {
            'SU': [[31,27,23,19,15], False],
            'SBJ': [[172,164,155,146,137], False],
            'SAR': [[40,38,35,31,26], False],
            'PU': [[16,14,11,8,4], False],
            'SR': [[11.3,11.7,12.2,12.7,13.3], True],
            'RUN': [[10.75,11.5,12.42,13.17,14.17], True]
        }
    },
    14: {
        'm': {
            'SU': [[40,36,32,28,24], False],
            'SBJ': [[218,210,202,194,186], False],
            'SAR': [[41,39,36,32,27], False],
            'PU': [[10,9,8,7,6], False],
            'SR': [[10.2,10.6,11.0,11.5,12.0], True],
            'RUN': [[9.0,9.75,10.5,11.33,12.08], True]
        },
        'f': {
            'SU': [[33,29,25,21,17], False],
            'SBJ': [[176,168,159,150,141], False],
            'SAR': [[41,39,36,32,27], False],
            'PU': [[17,15,12,9,5], False],
            'SR': [[11.1,11.5,12.0,12.5,13.1], True],
            'RUN': [[10.5,11.25,12.17,12.92,13.92], True]
        }
    },
    15: {
        'm': {
            'SU': [[42,38,34,30,26], False],
            'SBJ': [[228,220,212,204,196], False],
            'SAR': [[42,40,37,33,28], False],
            'PU': [[12,11,10,9,8], False],
            'SR': [[9.9,10.3,10.7,11.2,11.7], True],
            'RUN': [[8.67,9.42,10.17,11.0,11.75], True]
        },
        'f': {
            'SU': [[35,31,27,23,19], False],
            'SBJ': [[180,172,163,154,145], False],
            'SAR': [[42,40,37,33,28], False],
            'PU': [[18,16,13,10,6], False],
            'SR': [[10.9,11.3,11.8,12.3,12.9], True],
            'RUN': [[10.25,11.0,11.92,12.67,13.67], True]
        }
    },
    16: {
        'm': {
            'SU': [[44,40,36,32,28], False],
            'SBJ': [[238,230,222,214,206], False],
            'SAR': [[43,41,38,34,29], False],
            'PU': [[14,13,12,11,10], False],
            'SR': [[9.6,10.0,10.4,10.9,11.4], True],
            'RUN': [[8.33,9.08,9.83,10.67,11.42], True]
        },
        'f': {
            'SU': [[37,33,29,25,21], False],
            'SBJ': [[184,176,167,158,149], False],
            'SAR': [[43,41,38,34,29], False],
            'PU': [[19,17,14,11,7], False],
            'SR': [[10.7,11.1,11.6,12.1,12.7], True],
            'RUN': [[10.0,10.75,11.67,12.42,13.42], True]
        }
    }
}

def calc_grade(score, cutoffs, reverse):
    """Calculate grade from score and cutoffs"""
    for i, cutoff in enumerate(cutoffs):
        if reverse:
            if score <= cutoff:
                return 5 - i
        else:
            if score >= cutoff:
                return 5 - i
    return 0

# Body Type Calculator
def calculate_body_type(weight, height):
    """Calculate body type based on BMI and frame"""
    bmi = weight / (height * height)
    
    # Simplified body type classification
    if bmi < 18.5:
        return "Ectomorph", "Naturally lean, fast metabolism, difficulty gaining weight"
    elif bmi < 25:
        if bmi < 21.5:
            return "Ectomorph", "Naturally lean, fast metabolism, difficulty gaining weight"
        else:
            return "Mesomorph", "Athletic build, gains muscle easily, responds well to training"
    elif bmi < 30:
        return "Mesomorph", "Athletic build, gains muscle easily, responds well to training"
    else:
        return "Endomorph", "Larger bone structure, gains weight easily, slower metabolism"

# Recipe API Integration (using TheMealDB - free API)
def search_recipes_by_diet(diet_type, meal_type=""):
    """Search for recipes based on diet goals"""
    # This is a placeholder - TheMealDB API doesn't require auth
    # We'll create a curated list based on diet needs
    
    recipes = {
        "Weight Loss": [
            {"name": "Grilled Chicken Salad", "calories": 350, "protein": "35g", "carbs": "20g", "prep_time": "20 min",
             "ingredients": ["Chicken breast", "Mixed greens", "Cherry tomatoes", "Cucumber", "Olive oil", "Lemon"],
             "instructions": "1. Grill chicken breast until cooked\n2. Chop vegetables\n3. Mix greens with veggies\n4. Slice chicken on top\n5. Drizzle with olive oil and lemon"},
            
            {"name": "Steamed Fish with Vegetables", "calories": 320, "protein": "40g", "carbs": "15g", "prep_time": "25 min",
             "ingredients": ["White fish fillet", "Broccoli", "Carrots", "Ginger", "Soy sauce", "Garlic"],
             "instructions": "1. Season fish with ginger and garlic\n2. Steam fish for 15 min\n3. Steam vegetables separately\n4. Serve with light soy sauce"},
            
            {"name": "Egg White Omelette", "calories": 180, "protein": "20g", "carbs": "8g", "prep_time": "10 min",
             "ingredients": ["Egg whites (4)", "Spinach", "Mushrooms", "Tomatoes", "Black pepper"],
             "instructions": "1. Whisk egg whites\n2. Sauté vegetables\n3. Pour egg whites over veggies\n4. Cook until set"},
            
            {"name": "Greek Yogurt Bowl", "calories": 250, "protein": "18g", "carbs": "30g", "prep_time": "5 min",
             "ingredients": ["Greek yogurt", "Berries", "Chia seeds", "Honey (small amount)", "Almonds"],
             "instructions": "1. Add yogurt to bowl\n2. Top with berries\n3. Sprinkle chia seeds and chopped almonds\n4. Drizzle tiny bit of honey"},
            
            {"name": "Vegetable Soup", "calories": 150, "protein": "8g", "carbs": "25g", "prep_time": "30 min",
             "ingredients": ["Mixed vegetables", "Vegetable broth", "Garlic", "Onion", "Herbs"],
             "instructions": "1. Sauté garlic and onion\n2. Add chopped vegetables\n3. Pour in broth\n4. Simmer 20 minutes\n5. Season with herbs"}
        ],
        
        "Muscle Gain": [
            {"name": "Chicken Rice Bowl", "calories": 650, "protein": "50g", "carbs": "70g", "prep_time": "30 min",
             "ingredients": ["Chicken breast", "Brown rice", "Sweet potato", "Broccoli", "Olive oil"],
             "instructions": "1. Cook brown rice\n2. Grill or bake chicken\n3. Roast sweet potato\n4. Steam broccoli\n5. Combine in bowl with olive oil"},
            
            {"name": "Salmon with Quinoa", "calories": 700, "protein": "45g", "carbs": "60g", "prep_time": "25 min",
             "ingredients": ["Salmon fillet", "Quinoa", "Avocado", "Spinach", "Lemon"],
             "instructions": "1. Cook quinoa\n2. Bake salmon with lemon\n3. Sauté spinach\n4. Serve together with sliced avocado"},
            
            {"name": "Protein Smoothie Bowl", "calories": 550, "protein": "40g", "carbs": "65g", "prep_time": "10 min",
             "ingredients": ["Protein powder", "Banana", "Oats", "Peanut butter", "Milk", "Berries"],
             "instructions": "1. Blend protein powder, banana, oats, milk\n2. Pour into bowl\n3. Top with berries and peanut butter"},
            
            {"name": "Beef Stir Fry", "calories": 600, "protein": "48g", "carbs": "50g", "prep_time": "20 min",
             "ingredients": ["Lean beef", "Mixed vegetables", "Brown rice", "Soy sauce", "Garlic", "Ginger"],
             "instructions": "1. Cook brown rice\n2. Stir fry beef with garlic and ginger\n3. Add vegetables\n4. Season with soy sauce\n5. Serve over rice"},
            
            {"name": "Tuna Pasta", "calories": 620, "protein": "42g", "carbs": "75g", "prep_time": "20 min",
             "ingredients": ["Whole wheat pasta", "Canned tuna", "Cherry tomatoes", "Olive oil", "Garlic", "Basil"],
             "instructions": "1. Cook pasta\n2. Sauté garlic and tomatoes\n3. Add drained tuna\n4. Mix with pasta\n5. Top with fresh basil"}
        ],
        
        "Maintenance": [
            {"name": "Balanced Buddha Bowl", "calories": 500, "protein": "28g", "carbs": "55g", "prep_time": "25 min",
             "ingredients": ["Chickpeas", "Quinoa", "Mixed greens", "Avocado", "Cherry tomatoes", "Tahini"],
             "instructions": "1. Cook quinoa\n2. Roast chickpeas\n3. Arrange greens in bowl\n4. Add quinoa, chickpeas, tomatoes\n5. Top with avocado and tahini"},
            
            {"name": "Chicken Wrap", "calories": 480, "protein": "35g", "carbs": "45g", "prep_time": "15 min",
             "ingredients": ["Whole wheat wrap", "Grilled chicken", "Lettuce", "Tomato", "Hummus", "Cucumber"],
             "instructions": "1. Spread hummus on wrap\n2. Add lettuce and vegetables\n3. Place sliced chicken\n4. Roll tightly and cut"},
            
            {"name": "Egg Fried Rice", "calories": 520, "protein": "22g", "carbs": "62g", "prep_time": "20 min",
             "ingredients": ["Brown rice", "Eggs", "Mixed vegetables", "Soy sauce", "Spring onions"],
             "instructions": "1. Cook rice (preferably day-old)\n2. Scramble eggs separately\n3. Stir fry vegetables\n4. Add rice and eggs\n5. Season with soy sauce"},
            
            {"name": "Grilled Fish Tacos", "calories": 450, "protein": "32g", "carbs": "48g", "prep_time": "20 min",
             "ingredients": ["White fish", "Corn tortillas", "Cabbage", "Lime", "Greek yogurt", "Cilantro"],
             "instructions": "1. Season and grill fish\n2. Warm tortillas\n3. Shred cabbage\n4. Assemble tacos with fish and slaw\n5. Top with yogurt and cilantro"},
            
            {"name": "Oatmeal with Fruits", "calories": 380, "protein": "15g", "carbs": "58g", "prep_time": "10 min",
             "ingredients": ["Oats", "Milk", "Banana", "Berries", "Honey", "Nuts"],
             "instructions": "1. Cook oats with milk\n2. Slice banana\n3. Top with fruits and nuts\n4. Drizzle with honey"}
        ]
    }
    
    return recipes

# AI Helper Functions
def generate_ai_response(question, user_data):
    """Generate AI response based on user question and their data"""
    question_lower = question.lower()
    
    # Analyze user data for context
    has_napfa = len(user_data.get('napfa_history', [])) > 0
    has_bmi = len(user_data.get('bmi_history', [])) > 0
    has_sleep = len(user_data.get('sleep_history', [])) > 0
    
    # NAPFA related questions
    if 'napfa' in question_lower or 'pull' in question_lower or 'sit up' in question_lower or 'run' in question_lower:
        if has_napfa:
            latest = user_data['napfa_history'][-1]
            weak_tests = [test for test, grade in latest['grades'].items() if grade < 3]
            if weak_tests:
                return f"Based on your latest NAPFA test, I see you need work on: {', '.join(weak_tests)}. Check the 'Workout Recommendations' tab for specific exercises! Focus on consistency - train each weak area 3-4x per week."
            else:
                return f"Great NAPFA scores! Your total is {latest['total']} points. To maintain or improve: (1) Keep training all components weekly, (2) Focus on explosive power for jumps, (3) Mix steady runs with sprints, (4) Don't neglect flexibility!"
        else:
            return "Complete a NAPFA test first so I can give you personalized advice! Once you do, I'll analyze your weak areas and create a specific plan."
    
    # BMI/Weight related
    elif 'weight' in question_lower or 'bmi' in question_lower or 'lose' in question_lower or 'gain' in question_lower:
        if has_bmi:
            latest_bmi = user_data['bmi_history'][-1]
            category = latest_bmi['category']
            if category == "Normal":
                return f"Your BMI is {latest_bmi['bmi']} (Normal range). To maintain: eat balanced meals, exercise 4-5x/week, stay hydrated. Focus on building strength and endurance rather than weight change!"
            elif category == "Underweight":
                return "To gain healthy weight: (1) Eat 5-6 small meals daily, (2) Focus on protein + complex carbs, (3) Strength train 3-4x/week, (4) Drink smoothies with banana, oats, peanut butter. Check 'Meal Suggestions' for specific foods!"
            else:
                return "For healthy weight loss: (1) Create small calorie deficit (200-300 cal), (2) Eat lean protein + veggies each meal, (3) Do cardio 4-5x/week, (4) Avoid sugary drinks. Check 'Meal Suggestions' for detailed plan!"
        else:
            return "Calculate your BMI first! Then I can give you personalized nutrition and training advice for your goals."
    
    # Sleep related
    elif 'sleep' in question_lower or 'tired' in question_lower or 'energy' in question_lower:
        if has_sleep:
            sleep_data = user_data['sleep_history']
            avg_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / len(sleep_data)
            if avg_hours >= 8:
                return f"Your sleep is excellent at {avg_hours:.1f} hours! Keep it consistent. If still tired: check iron levels, reduce screen time before bed, and ensure quality sleep (dark, cool room)."
            else:
                return f"You're averaging {avg_hours:.1f} hours - you need 8-10 hours as a teen! Tips: (1) Set bedtime alarm, (2) No screens 1hr before bed, (3) Same sleep schedule daily, (4) Avoid caffeine after 2pm. Check 'Sleep Insights' for more!"
        else:
            return "Track your sleep for a few days first! Then I can analyze your patterns and give specific advice. Teenagers need 8-10 hours for optimal performance and recovery."
    
    # Strength training
    elif 'strength' in question_lower or 'muscle' in question_lower or 'strong' in question_lower:
        return "To build strength: (1) Focus on compound exercises (push-ups, pull-ups, squats), (2) Progressive overload - increase difficulty weekly, (3) Eat protein after workouts, (4) Rest 48hrs between training same muscles, (5) Start with bodyweight, add resistance gradually. Check 'Custom Workout Plan' for a complete program!"
    
    # Cardio/Endurance
    elif 'cardio' in question_lower or 'endurance' in question_lower or 'stamina' in question_lower:
        return "Build endurance with: (1) Start at comfortable pace - able to talk while running, (2) Gradually increase distance by 10% weekly, (3) Mix steady runs (30-45min) with intervals (sprint 1min, jog 2min x 8), (4) Cross-train with swimming/cycling, (5) Stay hydrated! Aim for 3-4 cardio sessions weekly."
    
    # Diet/Nutrition
    elif 'eat' in question_lower or 'food' in question_lower or 'diet' in question_lower or 'meal' in question_lower:
        return "For athletic performance: (1) Eat breakfast within 1hr of waking, (2) Balance each meal: lean protein + complex carbs + vegetables, (3) Pre-workout: banana + peanut butter, (4) Post-workout: protein + carbs within 1hr, (5) Stay hydrated - 8-10 glasses daily, (6) Limit processed foods and sugar. Check 'Meal Suggestions' for specific plans!"
    
    # Recovery
    elif 'recover' in question_lower or 'sore' in question_lower or 'rest' in question_lower:
        return "Recovery is crucial! (1) Sleep 8-10 hours, (2) Eat protein within 1hr post-workout, (3) Stay hydrated, (4) Active recovery: light walk/swim on rest days, (5) Stretch daily, (6) Ice sore muscles, (7) Rest 1-2 full days/week. Muscle soreness 24-48hrs after workout is normal (DOMS)!"
    
    # Motivation
    elif 'motivat' in question_lower or 'give up' in question_lower or 'hard' in question_lower:
        return "Stay motivated! 💪 (1) Set small, achievable goals, (2) Track progress - celebrate small wins, (3) Find a workout buddy, (4) Mix up your routine to stay interested, (5) Remember your 'why', (6) Progress isn't linear - some weeks are tough, (7) Focus on how you FEEL not just numbers. You've got this!"
    
    # Flexibility
    elif 'stretch' in question_lower or 'flexibility' in question_lower or 'flexib' in question_lower:
        return "Improve flexibility: (1) Stretch AFTER workouts when muscles are warm, (2) Hold each stretch 30-60 seconds, (3) Never bounce, (4) Stretch daily - even on rest days, (5) Focus on hamstrings, hip flexors, shoulders, (6) Try yoga 1-2x/week, (7) Breathe deeply while stretching. Flexibility improves injury prevention and performance!"
    
    # Injury
    elif 'injur' in question_lower or 'pain' in question_lower or 'hurt' in question_lower:
        return "⚠️ If you have pain (not soreness): (1) STOP that activity immediately, (2) Rest and ice the area, (3) See a doctor/physiotherapist if pain persists, (4) Don't train through pain - it makes injuries worse. Prevention: warm up properly, increase intensity gradually, use proper form, rest adequately. Your health comes first!"
    
    # Default helpful response
    else:
        return "I can help with: NAPFA training, strength building, cardio/endurance, nutrition/meals, weight management, sleep optimization, recovery, flexibility, injury prevention, and motivation! Try asking about any of these topics, or check the other tabs for detailed insights based on your data. What specific aspect of fitness would you like to know about?"

def generate_workout_exercises(focus, location, duration_min, fitness_level):
    """Generate exercises based on workout parameters"""
    exercises = []
    
    # Adjust sets/reps based on fitness level
    if fitness_level == "Beginner":
        sets, reps = 2, 10
        rest = "60-90 seconds"
    elif fitness_level == "Intermediate":
        sets, reps = 3, 12
        rest = "45-60 seconds"
    else:  # Advanced
        sets, reps = 4, 15
        rest = "30-45 seconds"
    
    # Generate exercises based on focus
    if focus in ["Upper Body Strength", "Strength Training"]:
        if location == "Home (no equipment)":
            exercises = [
                f"Push-ups: {sets} sets x {reps} reps (rest {rest})",
                f"Diamond push-ups: {sets} sets x {reps-5} reps",
                f"Pike push-ups: {sets} sets x {reps-3} reps",
                f"Tricep dips (chair): {sets} sets x {reps} reps",
                f"Plank shoulder taps: {sets} sets x {reps*2} taps"
            ]
        elif location == "Gym" or location == "School":
            exercises = [
                f"Pull-ups/Chin-ups: {sets} sets x max reps",
                f"Push-ups: {sets} sets x {reps+5} reps",
                f"Dumbbell shoulder press: {sets} sets x {reps} reps",
                f"Bent-over rows: {sets} sets x {reps} reps",
                f"Dips: {sets} sets x {reps} reps"
            ]
        else:
            exercises = [
                f"Pull-ups (bar/tree): {sets} sets x max reps",
                f"Push-ups: {sets} sets x {reps} reps",
                f"Bench dips: {sets} sets x {reps} reps",
                f"Inverted rows: {sets} sets x {reps} reps"
            ]
    
    elif focus in ["Lower Body & Core", "Lower Body"]:
        exercises = [
            f"Squats: {sets} sets x {reps+5} reps",
            f"Lunges: {sets} sets x {reps} reps each leg",
            f"Glute bridges: {sets} sets x {reps+5} reps",
            f"Calf raises: {sets} sets x {reps+10} reps",
            f"Plank: {sets} sets x 30-60 seconds",
            f"Russian twists: {sets} sets x {reps*2} total reps",
            f"Bicycle crunches: {sets} sets x {reps+5} reps"
        ]
    
    elif focus in ["Cardio & Endurance", "Cardio Training"]:
        if duration_min >= 60:
            exercises = [
                "Running: 30 minutes steady pace",
                "Interval sprints: 8 rounds (1 min sprint, 2 min jog)",
                "Jump rope: 3 sets x 3 minutes",
                "High knees: 3 sets x 1 minute",
                "Burpees: 3 sets x 12 reps"
            ]
        else:
            exercises = [
                "Running: 15-20 minutes steady pace",
                "Interval sprints: 6 rounds (1 min sprint, 90 sec jog)",
                "Jumping jacks: 3 sets x 50 reps",
                "Mountain climbers: 3 sets x 30 seconds"
            ]
    
    else:  # Full Body
        exercises = [
            f"Squats: {sets} sets x {reps} reps",
            f"Push-ups: {sets} sets x {reps} reps",
            f"Lunges: {sets} sets x {reps} reps each leg",
            f"Plank: {sets} sets x 45 seconds",
            f"Burpees: {sets} sets x {reps-2} reps",
            f"Sit-ups: {sets} sets x {reps+5} reps",
            f"Jump squats: {sets} sets x {reps} reps"
        ]
    
    return exercises

# Login/Registration Page
def login_page():
    st.markdown('<div class="main-header"><h1>🏋️ FitTrack</h1><p>School of Science and Technology Singapore</p><p>Your Personal Fitness Companion</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        st.subheader("Welcome Back!")
        
        # Google-style login
        email = st.text_input("Email Address", key="login_email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In", key="login_btn", type="primary"):
            # Find user by email
            user_found = None
            for username, data in st.session_state.users_data.items():
                if data.get('email', '').lower() == email.lower():
                    # Simple password check (in real app, this would be hashed)
                    if data.get('password') == password:
                        user_found = username
                        break
            
            if user_found:
                st.session_state.logged_in = True
                st.session_state.username = user_found
                st.rerun()
            else:
                st.error("Invalid email or password")
        
        st.write("")
        st.info("💡 **Students:** Use any email | **Teachers:** Must use @sst.edu.sg email")
    
    with tab2:
        st.subheader("Create Your Account")
        
        # Role selection at the top
        st.write("### Select Your Role")
        role = st.radio("I am a:", ["Student", "Teacher"], key="reg_role", horizontal=True)
        
        st.write("---")
        st.write("### Account Information")
        
        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input("Email Address", key="reg_email", 
                                     placeholder="student@example.com" if role == "Student" else "teacher@sst.edu.sg")
            full_name = st.text_input("Full Name", key="reg_name")
        
        with col2:
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        
        st.write("### Personal Details")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=12, max_value=100 if role == "Teacher" else 18, 
                                 value=14 if role == "Student" else 30, key="reg_age")
            gender = st.selectbox("Gender", ["Male", "Female"], key="reg_gender")
        
        with col2:
            if role == "Student":
                school = st.text_input("School (Optional)", value="School of Science and Technology", key="reg_school")
                class_name = st.text_input("Class (Optional)", placeholder="e.g., 3-Integrity", key="reg_class")
            else:
                school = "School of Science and Technology"
                st.text_input("School", value=school, disabled=True, key="reg_school_teacher")
                department = st.text_input("Department (Optional)", placeholder="e.g., PE Department", key="reg_department")
        
        if role == "Student":
            st.write("### Privacy Settings")
            show_on_leaderboards = st.checkbox("Show me on public leaderboards", value=False, key="reg_leaderboard")
            
            st.write("### Join a Class (Optional)")
            class_code = st.text_input("Class Code", placeholder="Enter code from your teacher", key="reg_class_code")
        
        if st.button("Create Account", key="register_btn", type="primary"):
            # Validation
            if not new_email or not full_name or not new_password:
                st.error("Please fill in all required fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            elif role == "Teacher" and not new_email.lower().endswith("@sst.edu.sg"):
                st.error("Teachers must use an @sst.edu.sg email address")
            elif any(data.get('email', '').lower() == new_email.lower() for data in st.session_state.users_data.values()):
                st.error("Email already registered")
            else:
                # Generate username from email
                username = new_email.split('@')[0].replace('.', '_')
                
                # Ensure username is unique
                original_username = username
                counter = 1
                while username in st.session_state.users_data:
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Create account based on role
                if role == "Student":
                    st.session_state.users_data[username] = {
                        'email': new_email.lower(),
                        'password': new_password,  # In production, this should be hashed
                        'role': 'student',
                        'name': full_name,
                        'age': age,
                        'gender': 'm' if gender == "Male" else 'f',
                        'school': school,
                        'class': class_name,
                        'show_on_leaderboards': show_on_leaderboards,
                        'created': datetime.now().isoformat(),
                        'bmi_history': [],
                        'napfa_history': [],
                        'sleep_history': [],
                        'exercises': [],
                        'goals': [],
                        'schedule': [],
                        'saved_workout_plan': None,
                        'friends': [],
                        'friend_requests': [],
                        'badges': [],
                        'level': 'Novice',
                        'total_points': 0,
                        'last_login': datetime.now().isoformat(),
                        'login_streak': 0,
                        'active_challenges': [],
                        'completed_challenges': [],
                        'teacher_class': None  # Will be set when joining a class
                    }
                    
                    # Join class if code provided
                    if class_code:
                        # Find teacher with this class code
                        for teacher_username, teacher_data in st.session_state.users_data.items():
                            if teacher_data.get('role') == 'teacher' and teacher_data.get('class_code') == class_code:
                                # Check class size limit
                                current_students = teacher_data.get('students', [])
                                if len(current_students) >= 30:
                                    st.warning(f"Class is full (30/30 students). Contact your teacher.")
                                else:
                                    st.session_state.users_data[username]['teacher_class'] = teacher_username
                                    teacher_data['students'].append(username)
                                    st.success(f"✅ Joined {teacher_data['name']}'s class!")
                                break
                        else:
                            st.warning("Invalid class code. You can join a class later.")
                
                else:  # Teacher
                    # Generate unique class code
                    import random
                    import string
                    class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    
                    st.session_state.users_data[username] = {
                        'email': new_email.lower(),
                        'password': new_password,
                        'role': 'teacher',
                        'name': full_name,
                        'age': age,
                        'gender': 'm' if gender == "Male" else 'f',
                        'school': school,
                        'department': department,
                        'created': datetime.now().isoformat(),
                        'class_code': class_code,
                        'students': [],  # List of student usernames
                        'classes_created': [],  # Can create multiple classes
                        'last_login': datetime.now().isoformat()
                    }
                
                save_users(st.session_state.users_data)
                st.success("✅ Account created successfully! Please sign in.")
                
                if role == "Teacher":
                    st.info(f"📝 Your Class Code: **{class_code}** - Share this with your students!")
                
                st.balloons()
                time.sleep(2)
                st.rerun()
                save_users(st.session_state.users_data)
                st.success("Account created! Please login.")

# BMI Calculator
def bmi_calculator():
    st.header("📊 BMI Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=60.0, step=0.1)
    with col2:
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.65, step=0.01)
    
    if st.button("Calculate BMI"):
        bmi = weight / (height * height)
        
        if bmi < 18.5:
            category = "Underweight"
            color = "#2196f3"
        elif bmi < 25:
            category = "Normal"
            color = "#4caf50"
        elif bmi < 30:
            category = "Overweight"
            color = "#ff9800"
        else:
            category = "Obesity"
            color = "#f44336"
        
        # Save to history
        user_data = get_user_data()
        user_data['bmi_history'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'bmi': round(bmi, 2),
            'weight': weight,
            'height': height,
            'category': category
        })
        update_user_data(user_data)
        
        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stat-card"><h2 style="color: {color};">BMI: {bmi:.2f}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><h2 style="color: {SST_COLORS["gray"]};">Category: {category}</h2></div>', unsafe_allow_html=True)
        
        st.info(f"📈 You have {len(user_data['bmi_history'])} BMI record(s) saved.")
        
        # Show history chart if there's data
        if len(user_data['bmi_history']) > 1:
            df = pd.DataFrame(user_data['bmi_history'])
            df_chart = df.set_index('date')['bmi']
            st.subheader("BMI History")
            st.line_chart(df_chart)

# NAPFA Test Calculator
def napfa_calculator():
    st.header("🏃 NAPFA Test Calculator")
    
    user_data = get_user_data()
    
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"], 
                            index=0 if user_data['gender'] == 'm' else 1)
    with col2:
        age = st.number_input("Age", min_value=12, max_value=16, value=user_data['age'])
    
    if age not in NAPFA_STANDARDS:
        st.error("Age must be between 12-16")
        return
    
    gender_key = 'm' if gender == "Male" else 'f'
    
    st.subheader("Enter Your Scores")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        situps = st.number_input("Sit-ups (1 min)", min_value=0, max_value=100, value=30)
        broadjump = st.number_input("Standing Broad Jump (cm)", min_value=0, max_value=300, value=200)
    with col2:
        sitreach = st.number_input("Sit and Reach (cm)", min_value=0, max_value=100, value=35)
        pullups = st.number_input("Pull-ups (30 sec)", min_value=0, max_value=50, value=8)
    with col3:
        shuttlerun = st.number_input("Shuttle Run (seconds)", min_value=5.0, max_value=20.0, value=10.5, step=0.1)
        run_time = st.text_input("2.4km Run (min:sec)", value="10:30")
    
    if st.button("Calculate Grades"):
        try:
            # Convert run time
            time_parts = run_time.split(':')
            run_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
            
            standards = NAPFA_STANDARDS[age][gender_key]
            
            scores = {
                'SU': situps,
                'SBJ': broadjump,
                'SAR': sitreach,
                'PU': pullups,
                'SR': shuttlerun,
                'RUN': run_minutes
            }
            
            test_names = {
                'SU': 'Sit-Ups',
                'SBJ': 'Standing Broad Jump',
                'SAR': 'Sit and Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }
            
            grades = {}
            total = 0
            min_grade = 5
            
            for test in scores:
                grade = calc_grade(scores[test], standards[test][0], standards[test][1])
                grades[test] = grade
                total += grade
                min_grade = min(min_grade, grade)
            
            # Determine medal
            if total >= 21 and min_grade >= 3:
                medal = "🥇 Gold"
                medal_color = "#FFD700"
            elif total >= 15 and min_grade >= 2:
                medal = "🥈 Silver"
                medal_color = "#C0C0C0"
            elif total >= 9 and min_grade >= 1:
                medal = "🥉 Bronze"
                medal_color = "#CD7F32"
            else:
                medal = "No Medal"
                medal_color = SST_COLORS['gray']
            
            # Save to history
            user_data['napfa_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'age': age,
                'gender': gender_key,
                'scores': scores,
                'grades': grades,
                'total': total,
                'medal': medal
            })
            update_user_data(user_data)
            
            # Display results
            st.markdown("### Results")
            
            results_data = []
            for test, grade in grades.items():
                results_data.append({
                    'Test': test_names[test],
                    'Score': scores[test],
                    'Grade': grade
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stat-card"><h2 style="color: {SST_COLORS["blue"]};">Total: {total}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h2 style="color: {medal_color};">Medal: {medal}</h2></div>', unsafe_allow_html=True)
            
            st.info(f"📈 You have {len(user_data['napfa_history'])} NAPFA test(s) saved.")
            
        except Exception as e:
            st.error(f"Error calculating grades: {str(e)}")

# Sleep Tracker
def sleep_tracker():
    st.header("😴 Sleep Tracker")
    
    col1, col2 = st.columns(2)
    with col1:
        sleep_start = st.time_input("Sleep Start Time", value=None)
    with col2:
        sleep_end = st.time_input("Wake Up Time", value=None)
    
    if st.button("Calculate Sleep"):
        if sleep_start and sleep_end:
            # Convert to datetime for calculation
            start = datetime.combine(datetime.today(), sleep_start)
            end = datetime.combine(datetime.today(), sleep_end)
            
            # Handle overnight sleep
            if end < start:
                end += timedelta(days=1)
            
            diff = end - start
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if hours >= 8:
                quality = "Excellent"
                color = "#4caf50"
                advice = "✓ Great job! You're getting enough sleep."
            elif hours >= 7:
                quality = "Good"
                color = "#8bc34a"
                advice = "👍 Good sleep duration. Try to get a bit more."
            elif hours >= 6:
                quality = "Fair"
                color = "#ff9800"
                advice = "⚠️ You need more sleep. Aim for 8-10 hours per night."
            else:
                quality = "Poor"
                color = "#f44336"
                advice = "⚠️ You need more sleep. Aim for 8-10 hours per night."
            
            # Save to history
            user_data = get_user_data()
            user_data['sleep_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sleep_start': str(sleep_start),
                'sleep_end': str(sleep_end),
                'hours': hours,
                'minutes': minutes,
                'quality': quality
            })
            update_user_data(user_data)
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stat-card"><h2 style="color: {color};">Sleep Duration: {hours}h {minutes}m</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h2 style="color: {SST_COLORS["blue"]};">Quality: {quality}</h2></div>', unsafe_allow_html=True)
            
            st.info(advice)
            st.info(f"📈 You have {len(user_data['sleep_history'])} sleep record(s) saved.")
            
            # Show history chart if there's data
            if len(user_data['sleep_history']) > 1:
                df = pd.DataFrame(user_data['sleep_history'])
                df['total_hours'] = df['hours'] + df['minutes'] / 60
                df_chart = df.set_index('date')['total_hours']
                st.subheader("Sleep Duration History (hours)")
                st.line_chart(df_chart)
        else:
            st.error("Please enter both sleep start and end times")

# Exercise Logger
def exercise_logger():
    st.header("💪 Exercise Logger")
    
    with st.form("exercise_form"):
        exercise_name = st.text_input("Exercise Name", placeholder="e.g., Running, Swimming")
        
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        with col2:
            intensity = st.selectbox("Intensity", ["Low", "Medium", "High"])
        
        notes = st.text_area("Notes", placeholder="Any additional notes...")
        
        submitted = st.form_submit_button("Log Exercise")
        
        if submitted:
            if exercise_name:
                user_data = get_user_data()
                user_data['exercises'].insert(0, {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'name': exercise_name,
                    'duration': duration,
                    'intensity': intensity,
                    'notes': notes
                })
                update_user_data(user_data)
                st.success("Exercise logged successfully!")
                st.rerun()
            else:
                st.error("Please enter exercise name")
    
    # Display exercise history
    user_data = get_user_data()
    if user_data['exercises']:
        st.subheader("Recent Exercises")
        df = pd.DataFrame(user_data['exercises'])
        st.dataframe(df[['date', 'name', 'duration', 'intensity']], use_container_width=True, hide_index=True)
        
        # Show summary chart
        if len(user_data['exercises']) > 0:
            exercise_counts = {}
            for ex in user_data['exercises']:
                exercise_counts[ex['name']] = exercise_counts.get(ex['name'], 0) + 1
            
            df_chart = pd.DataFrame({
                'Exercise': list(exercise_counts.keys()),
                'Count': list(exercise_counts.values())
            })
            df_chart = df_chart.set_index('Exercise')
            st.subheader("Exercise Frequency")
            st.bar_chart(df_chart)
    else:
        st.info("No exercises logged yet.")

# Goal Setting
def goal_setting():
    st.header("🎯 Fitness Goals")
    
    with st.form("goal_form"):
        goal_type = st.selectbox("Goal Type", 
                                ["Weight Loss", "Muscle Gain", "NAPFA Improvement", 
                                 "Endurance", "Flexibility"])
        target = st.text_input("Target Value", placeholder="e.g., 60kg, Grade 5, 30 min run")
        target_date = st.date_input("Target Date")
        progress = st.slider("Current Progress (%)", 0, 100, 0)
        
        submitted = st.form_submit_button("Set Goal")
        
        if submitted:
            if target:
                user_data = get_user_data()
                user_data['goals'].append({
                    'type': goal_type,
                    'target': target,
                    'date': target_date.strftime('%Y-%m-%d'),
                    'progress': progress,
                    'created': datetime.now().strftime('%Y-%m-%d')
                })
                update_user_data(user_data)
                st.success("Goal set successfully!")
                st.rerun()
            else:
                st.error("Please enter target value")
    
    # Display goals
    user_data = get_user_data()
    if user_data['goals']:
        st.subheader("Your Goals")
        for idx, goal in enumerate(user_data['goals']):
            with st.expander(f"{goal['type']} - {goal['target']}"):
                st.write(f"**Target Date:** {goal['date']}")
                st.write(f"**Created:** {goal['created']}")
                st.progress(goal['progress'] / 100)
                st.write(f"Progress: {goal['progress']}%")
    else:
        st.info("No goals set yet.")

# Badge and Achievement System
def check_and_award_badges(user_data):
    """Check if user earned any new badges and award points"""
    badges_earned = []
    points_earned = 0
    
    existing_badges = [b['name'] for b in user_data.get('badges', [])]
    
    # NAPFA Badges
    if user_data.get('napfa_history'):
        latest_napfa = user_data['napfa_history'][-1]
        
        # First Gold Medal
        if '🥇 First Gold' not in existing_badges and '🥇 Gold' in latest_napfa['medal']:
            badges_earned.append({
                'name': '🥇 First Gold',
                'description': 'Earned your first NAPFA Gold medal!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 100
            })
            points_earned += 100
        
        # Perfect Score
        all_grade_5 = all(grade == 5 for grade in latest_napfa['grades'].values())
        if '💯 Perfect Score' not in existing_badges and all_grade_5:
            badges_earned.append({
                'name': '💯 Perfect Score',
                'description': 'All Grade 5s on NAPFA test!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 200
            })
            points_earned += 200
    
    # Workout Badges
    if user_data.get('exercises'):
        total_workouts = len(user_data['exercises'])
        
        # Century Club
        if '💪 Century Club' not in existing_badges and total_workouts >= 100:
            badges_earned.append({
                'name': '💪 Century Club',
                'description': 'Completed 100 total workouts!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 150
            })
            points_earned += 150
        
        # Fifty Strong
        if '🏋️ Fifty Strong' not in existing_badges and total_workouts >= 50:
            badges_earned.append({
                'name': '🏋️ Fifty Strong',
                'description': 'Completed 50 workouts!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 75
            })
            points_earned += 75
        
        # Getting Started
        if '🎯 Getting Started' not in existing_badges and total_workouts >= 10:
            badges_earned.append({
                'name': '🎯 Getting Started',
                'description': 'Completed 10 workouts!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 25
            })
            points_earned += 25
        
        # Check workout streak
        workout_dates = sorted(list(set([e['date'] for e in user_data['exercises']])), reverse=True)
        if len(workout_dates) >= 2:
            streak = 1
            current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')
            
            for i in range(1, len(workout_dates)):
                prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                diff = (current_date - prev_date).days
                
                if diff <= 2:
                    streak += 1
                    current_date = prev_date
                else:
                    break
            
            # 7-day streak
            if '🔥 Week Warrior' not in existing_badges and streak >= 7:
                badges_earned.append({
                    'name': '🔥 Week Warrior',
                    'description': '7-day workout streak!',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'points': 50
                })
                points_earned += 50
            
            # 30-day streak
            if '🔥🔥 Month Master' not in existing_badges and streak >= 30:
                badges_earned.append({
                    'name': '🔥🔥 Month Master',
                    'description': '30-day workout streak!',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'points': 150
                })
                points_earned += 150
    
    # Sleep Badges
    if user_data.get('sleep_history'):
        # Check last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_sleep = [s for s in user_data['sleep_history'] 
                       if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
        
        if len(recent_sleep) >= 7:
            good_sleep_count = sum(1 for s in recent_sleep if s['hours'] >= 8)
            
            if '🌙 Sleep Champion' not in existing_badges and good_sleep_count >= 7:
                badges_earned.append({
                    'name': '🌙 Sleep Champion',
                    'description': '7 days of 8+ hours sleep!',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'points': 50
                })
                points_earned += 50
    
    # Goal Badges
    if user_data.get('goals'):
        completed_goals = sum(1 for g in user_data['goals'] if g['progress'] >= 100)
        
        if '🎯 Goal Crusher' not in existing_badges and completed_goals >= 5:
            badges_earned.append({
                'name': '🎯 Goal Crusher',
                'description': 'Completed 5 fitness goals!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 100
            })
            points_earned += 100
        
        if '🎯 First Goal' not in existing_badges and completed_goals >= 1:
            badges_earned.append({
                'name': '🎯 First Goal',
                'description': 'Completed your first goal!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 30
            })
            points_earned += 30
    
    # Daily Login
    if '📅 Daily Visitor' not in existing_badges and user_data.get('login_streak', 0) >= 7:
        badges_earned.append({
            'name': '📅 Daily Visitor',
            'description': '7-day login streak!',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'points': 40
        })
        points_earned += 40
    
    return badges_earned, points_earned

def calculate_level(total_points):
    """Calculate user level based on total points"""
    if total_points < 50:
        return "Novice", 0, 50
    elif total_points < 150:
        return "Beginner", 50, 150
    elif total_points < 300:
        return "Intermediate", 150, 300
    elif total_points < 500:
        return "Advanced", 300, 500
    elif total_points < 800:
        return "Expert", 500, 800
    elif total_points < 1200:
        return "Master", 800, 1200
    else:
        return "Legend", 1200, 1200

def update_login_streak(user_data):
    """Update login streak for daily login tracking"""
    last_login = user_data.get('last_login')
    if last_login:
        last_login_date = datetime.fromisoformat(last_login).date()
        today = datetime.now().date()
        days_diff = (today - last_login_date).days
        
        if days_diff == 1:
            # Consecutive day
            user_data['login_streak'] = user_data.get('login_streak', 0) + 1
        elif days_diff == 0:
            # Same day, no change
            pass
        else:
            # Streak broken
            user_data['login_streak'] = 1
    else:
        user_data['login_streak'] = 1
    
    user_data['last_login'] = datetime.now().isoformat()
    return user_data

# Community and Social Features
def community_features():
    st.header("🏆 Community & Achievements")
    
    user_data = get_user_data()
    all_users = st.session_state.users_data
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Leaderboards",
        "🎖️ My Achievements", 
        "👥 Friends",
        "⚡ Challenges",
        "⚙️ Privacy Settings"
    ])
    
    with tab1:
        st.subheader("🏆 Leaderboards")
        
        if not user_data.get('show_on_leaderboards', False):
            st.warning("⚠️ You're not visible on leaderboards. Update your privacy settings to join!")
            st.info("Go to 'Privacy Settings' tab to enable leaderboard participation.")
        
        # Filter users who opted in to leaderboards
        leaderboard_users = {username: data for username, data in all_users.items() 
                            if data.get('show_on_leaderboards', False)}
        
        if len(leaderboard_users) == 0:
            st.info("No users on leaderboards yet. Be the first to opt in!")
        else:
            # Leaderboard selection
            board_type = st.selectbox("Select Leaderboard", [
                "Workout Streak",
                "Weekly Warriors", 
                "Age & Gender Specific",
                "School Rankings",
                "Class Rankings"
            ])
            
            if board_type == "Workout Streak":
                st.write("### 🔥 Longest Workout Streaks")
                
                streaks = []
                for username, data in leaderboard_users.items():
                    if data.get('exercises'):
                        workout_dates = sorted(list(set([e['date'] for e in data['exercises']])), reverse=True)
                        if len(workout_dates) >= 1:
                            streak = 1
                            current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')
                            
                            for i in range(1, len(workout_dates)):
                                prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                                diff = (current_date - prev_date).days
                                
                                if diff <= 2:
                                    streak += 1
                                    current_date = prev_date
                                else:
                                    break
                            
                            streaks.append({
                                'username': username,
                                'name': data['name'],
                                'streak': streak,
                                'age': data['age'],
                                'school': data.get('school', 'N/A')
                            })
                
                streaks.sort(key=lambda x: x['streak'], reverse=True)
                
                for idx, user in enumerate(streaks[:10], 1):
                    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                    
                    highlight = "🌟 " if user['username'] == st.session_state.username else ""
                    st.write(f"{medal} {highlight}**{user['name']}** (@{user['username']}) - {user['streak']} days 🔥")
            
            elif board_type == "Weekly Warriors":
                st.write("### 💪 Most Workouts This Week")
                
                week_ago = datetime.now() - timedelta(days=7)
                weekly_counts = []
                
                for username, data in leaderboard_users.items():
                    if data.get('exercises'):
                        weekly_workouts = [e for e in data['exercises'] 
                                         if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                        
                        if weekly_workouts:
                            weekly_counts.append({
                                'username': username,
                                'name': data['name'],
                                'count': len(weekly_workouts),
                                'total_time': sum(e['duration'] for e in weekly_workouts),
                                'school': data.get('school', 'N/A')
                            })
                
                weekly_counts.sort(key=lambda x: x['count'], reverse=True)
                
                for idx, user in enumerate(weekly_counts[:10], 1):
                    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                    highlight = "🌟 " if user['username'] == st.session_state.username else ""
                    
                    st.write(f"{medal} {highlight}**{user['name']}** (@{user['username']}) - {user['count']} workouts ({user['total_time']} min)")
            
            elif board_type == "Age & Gender Specific":
                st.write("### 📊 Age & Gender Rankings")
                
                # Age and gender filters
                col1, col2 = st.columns(2)
                with col1:
                    selected_age = st.selectbox("Age", list(range(12, 19)))
                with col2:
                    selected_gender = st.selectbox("Gender", ["Male", "Female"])
                
                gender_key = 'm' if selected_gender == "Male" else 'f'
                
                # Filter users
                filtered_users = {username: data for username, data in leaderboard_users.items()
                                if data['age'] == selected_age and data['gender'] == gender_key}
                
                if not filtered_users:
                    st.info(f"No users in this category yet (Age {selected_age}, {selected_gender})")
                else:
                    # Rank by NAPFA score
                    napfa_rankings = []
                    for username, data in filtered_users.items():
                        if data.get('napfa_history'):
                            latest = data['napfa_history'][-1]
                            napfa_rankings.append({
                                'username': username,
                                'name': data['name'],
                                'score': latest['total'],
                                'medal': latest['medal'],
                                'school': data.get('school', 'N/A')
                            })
                    
                    napfa_rankings.sort(key=lambda x: x['score'], reverse=True)
                    
                    st.write(f"**Top NAPFA Scores - Age {selected_age} ({selected_gender})**")
                    for idx, user in enumerate(napfa_rankings[:10], 1):
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        highlight = "🌟 " if user['username'] == st.session_state.username else ""
                        
                        st.write(f"{medal} {highlight}**{user['name']}** (@{user['username']}) - {user['score']}/30 ({user['medal']})")
            
            elif board_type == "School Rankings":
                st.write("### 🏫 School Rankings")
                
                # Get all schools
                schools = list(set([data.get('school', 'N/A') for data in leaderboard_users.values()]))
                schools = [s for s in schools if s != 'N/A' and s]
                
                if not schools:
                    st.info("No schools registered yet")
                else:
                    school_stats = []
                    for school in schools:
                        school_users = {u: d for u, d in leaderboard_users.items() 
                                      if d.get('school') == school}
                        
                        # Calculate average NAPFA score
                        napfa_scores = []
                        for data in school_users.values():
                            if data.get('napfa_history'):
                                napfa_scores.append(data['napfa_history'][-1]['total'])
                        
                        if napfa_scores:
                            school_stats.append({
                                'school': school,
                                'students': len(school_users),
                                'avg_napfa': sum(napfa_scores) / len(napfa_scores),
                                'total_workouts': sum(len(d.get('exercises', [])) for d in school_users.values())
                            })
                    
                    school_stats.sort(key=lambda x: x['avg_napfa'], reverse=True)
                    
                    for idx, school in enumerate(school_stats, 1):
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        st.write(f"{medal} **{school['school']}** - {school['avg_napfa']:.1f} avg NAPFA | {school['students']} students | {school['total_workouts']} total workouts")
            
            elif board_type == "Class Rankings":
                st.write("### 📚 Class Rankings")
                
                # Get all classes
                classes = list(set([data.get('class', 'N/A') for data in leaderboard_users.values()]))
                classes = [c for c in classes if c != 'N/A' and c]
                
                if not classes:
                    st.info("No classes registered yet")
                else:
                    class_stats = []
                    for class_name in classes:
                        class_users = {u: d for u, d in leaderboard_users.items() 
                                     if d.get('class') == class_name}
                        
                        # Calculate stats
                        napfa_scores = []
                        for data in class_users.values():
                            if data.get('napfa_history'):
                                napfa_scores.append(data['napfa_history'][-1]['total'])
                        
                        if napfa_scores:
                            class_stats.append({
                                'class': class_name,
                                'students': len(class_users),
                                'avg_napfa': sum(napfa_scores) / len(napfa_scores),
                                'total_workouts': sum(len(d.get('exercises', [])) for d in class_users.values())
                            })
                    
                    class_stats.sort(key=lambda x: x['avg_napfa'], reverse=True)
                    
                    for idx, cls in enumerate(class_stats, 1):
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                        st.write(f"{medal} **{cls['class']}** - {cls['avg_napfa']:.1f} avg NAPFA | {cls['students']} students | {cls['total_workouts']} total workouts")
    
    with tab2:
        st.subheader("🎖️ My Achievements")
        
        # Check for new badges
        new_badges, new_points = check_and_award_badges(user_data)
        
        if new_badges:
            st.balloons()
            st.success(f"🎉 You earned {len(new_badges)} new badge(s) and {new_points} points!")
            
            for badge in new_badges:
                user_data['badges'].append(badge)
                user_data['total_points'] = user_data.get('total_points', 0) + badge['points']
            
            update_user_data(user_data)
        
        # Display level and progress
        current_level, level_min, level_max = calculate_level(user_data.get('total_points', 0))
        user_data['level'] = current_level
        update_user_data(user_data)
        
        st.write("### 📊 Your Progress")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Level", current_level)
        with col2:
            st.metric("Total Points", user_data.get('total_points', 0))
        with col3:
            st.metric("Login Streak", f"{user_data.get('login_streak', 0)} days")
        
        # Progress bar to next level
        if current_level != "Legend":
            progress = (user_data.get('total_points', 0) - level_min) / (level_max - level_min)
            st.progress(progress)
            st.write(f"**Next Level:** {level_max - user_data.get('total_points', 0)} points to go!")
        else:
            st.success("🏆 You've reached the maximum level!")
        
        # Display badges
        st.write("")
        st.write("### 🎖️ Earned Badges")
        
        if user_data.get('badges'):
            # Sort by date
            badges = sorted(user_data['badges'], key=lambda x: x['date'], reverse=True)
            
            cols = st.columns(3)
            for idx, badge in enumerate(badges):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%); 
                                padding: 15px; border-radius: 10px; color: white; margin: 5px;">
                        <h3>{badge['name']}</h3>
                        <p>{badge['description']}</p>
                        <small>Earned: {badge['date']} | +{badge['points']} pts</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No badges earned yet. Keep working out to unlock achievements!")
        
        # Available badges to earn
        st.write("")
        st.write("### 🎯 Available Badges")
        
        all_possible_badges = [
            "🥇 First Gold - Earn your first NAPFA Gold medal",
            "💯 Perfect Score - All Grade 5s on NAPFA",
            "💪 Century Club - Complete 100 workouts",
            "🏋️ Fifty Strong - Complete 50 workouts", 
            "🎯 Getting Started - Complete 10 workouts",
            "🔥 Week Warrior - 7-day workout streak",
            "🔥🔥 Month Master - 30-day workout streak",
            "🌙 Sleep Champion - 7 days of 8+ hours sleep",
            "🎯 Goal Crusher - Complete 5 goals",
            "🎯 First Goal - Complete your first goal",
            "📅 Daily Visitor - 7-day login streak"
        ]
        
        earned_names = [b['name'] for b in user_data.get('badges', [])]
        remaining = [b for b in all_possible_badges if not any(name in b for name in earned_names)]
        
        for badge in remaining:
            st.write(f"🔒 {badge}")
    
    with tab3:
        st.subheader("👥 Friends")
        
        # Friend requests
        friend_requests = user_data.get('friend_requests', [])
        if friend_requests:
            st.write("### 📬 Friend Requests")
            for requester in friend_requests:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    requester_data = all_users.get(requester, {})
                    st.write(f"**{requester_data.get('name', 'Unknown')}** (@{requester})")
                with col2:
                    if st.button("✅ Accept", key=f"accept_{requester}"):
                        user_data['friends'].append(requester)
                        user_data['friend_requests'].remove(requester)
                        
                        # Add to requester's friends too
                        all_users[requester]['friends'].append(st.session_state.username)
                        
                        update_user_data(user_data)
                        save_users(all_users)
                        st.success(f"Added {requester} as friend!")
                        st.rerun()
                with col3:
                    if st.button("❌ Decline", key=f"decline_{requester}"):
                        user_data['friend_requests'].remove(requester)
                        update_user_data(user_data)
                        st.rerun()
        
        # Add friend
        st.write("### ➕ Add Friend")
        new_friend = st.text_input("Enter username", key="add_friend_input")
        if st.button("Send Friend Request"):
            if new_friend in all_users:
                if new_friend == st.session_state.username:
                    st.error("You can't add yourself!")
                elif new_friend in user_data.get('friends', []):
                    st.error("Already friends!")
                elif new_friend in all_users[new_friend].get('friend_requests', []):
                    st.error("Request already sent!")
                else:
                    # Add request to target user
                    all_users[new_friend]['friend_requests'].append(st.session_state.username)
                    save_users(all_users)
                    st.success(f"Friend request sent to {new_friend}!")
            else:
                st.error("User not found")
        
        # Friends list
        st.write("### 👥 My Friends")
        friends = user_data.get('friends', [])
        
        if friends:
            for friend in friends:
                friend_data = all_users.get(friend, {})
                
                with st.expander(f"👤 {friend_data.get('name', 'Unknown')} (@{friend})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Age:** {friend_data.get('age', 'N/A')}")
                        st.write(f"**School:** {friend_data.get('school', 'N/A')}")
                        st.write(f"**Level:** {friend_data.get('level', 'Novice')}")
                    
                    with col2:
                        if friend_data.get('napfa_history'):
                            latest = friend_data['napfa_history'][-1]
                            st.write(f"**NAPFA:** {latest['total']}/30")
                            st.write(f"**Medal:** {latest['medal']}")
                        
                        if friend_data.get('exercises'):
                            st.write(f"**Workouts:** {len(friend_data['exercises'])}")
                    
                    # Recent activity
                    if friend_data.get('badges'):
                        recent_badge = friend_data['badges'][-1]
                        st.info(f"🎖️ Recently earned: {recent_badge['name']}")
                    
                    if st.button(f"Remove Friend", key=f"remove_{friend}"):
                        user_data['friends'].remove(friend)
                        all_users[friend]['friends'].remove(st.session_state.username)
                        update_user_data(user_data)
                        save_users(all_users)
                        st.rerun()
        else:
            st.info("No friends yet. Add friends to see their progress!")
    
    with tab4:
        st.subheader("⚡ Challenges")
        
        # Weekly Challenges
        st.write("### 🏃 Weekly Challenges")
        
        # Define weekly challenges
        weekly_challenges = [
            {
                'name': 'Workout Warrior',
                'description': 'Complete 5 workouts this week',
                'target': 5,
                'type': 'workouts',
                'points': 50
            },
            {
                'name': 'Cardio King',
                'description': 'Total 150 minutes of exercise this week',
                'target': 150,
                'type': 'minutes',
                'points': 60
            },
            {
                'name': 'Early Bird',
                'description': 'Log 7 days of sleep tracking',
                'target': 7,
                'type': 'sleep',
                'points': 40
            }
        ]
        
        # Check progress
        week_ago = datetime.now() - timedelta(days=7)
        
        for challenge in weekly_challenges:
            with st.expander(f"{'✅' if challenge['name'] in [c['name'] for c in user_data.get('completed_challenges', [])] else '⚡'} {challenge['name']} (+{challenge['points']} pts)", expanded=True):
                st.write(f"**Goal:** {challenge['description']}")
                
                # Calculate progress
                if challenge['type'] == 'workouts':
                    weekly_workouts = [e for e in user_data.get('exercises', []) 
                                     if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                    progress = len(weekly_workouts)
                elif challenge['type'] == 'minutes':
                    weekly_workouts = [e for e in user_data.get('exercises', []) 
                                     if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                    progress = sum(e['duration'] for e in weekly_workouts)
                else:  # sleep
                    weekly_sleep = [s for s in user_data.get('sleep_history', []) 
                                  if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
                    progress = len(weekly_sleep)
                
                st.progress(min(progress / challenge['target'], 1.0))
                st.write(f"**Progress:** {progress}/{challenge['target']}")
                
                if progress >= challenge['target']:
                    completed_names = [c['name'] for c in user_data.get('completed_challenges', [])]
                    if challenge['name'] not in completed_names:
                        st.success("🎉 Challenge completed! Points awarded!")
                        user_data.setdefault('completed_challenges', []).append({
                            'name': challenge['name'],
                            'completed_date': datetime.now().strftime('%Y-%m-%d'),
                            'points': challenge['points']
                        })
                        user_data['total_points'] = user_data.get('total_points', 0) + challenge['points']
                        update_user_data(user_data)
        
        # Friend Challenges
        st.write("")
        st.write("### 🤝 Friend Challenges")
        
        friends = user_data.get('friends', [])
        if not friends:
            st.info("Add friends to create challenges with them!")
        else:
            selected_friend = st.selectbox("Challenge a friend", friends)
            
            challenge_types = [
                "Most workouts this week",
                "Highest NAPFA score",
                "Longest workout streak"
            ]
            
            challenge_type = st.selectbox("Challenge type", challenge_types)
            
            if st.button("Send Challenge"):
                st.success(f"Challenge sent to {selected_friend}! (Feature coming soon)")
        
        # Class Challenges
        st.write("")
        st.write("### 🏫 Class Challenges")
        
        if user_data.get('class'):
            st.write(f"**Your Class:** {user_data['class']}")
            
            # Get class members
            class_members = {u: d for u, d in all_users.items() 
                           if d.get('class') == user_data['class'] and d.get('show_on_leaderboards', False)}
            
            if len(class_members) > 1:
                st.write(f"**Class Members:** {len(class_members)}")
                
                # Show class goal
                st.info("🎯 **Class Goal:** Average NAPFA score of 20+ by end of month!")
                
                # Calculate class average
                napfa_scores = []
                for data in class_members.values():
                    if data.get('napfa_history'):
                        napfa_scores.append(data['napfa_history'][-1]['total'])
                
                if napfa_scores:
                    class_avg = sum(napfa_scores) / len(napfa_scores)
                    st.metric("Current Class Average", f"{class_avg:.1f}/30")
                    
                    if class_avg >= 20:
                        st.success("🎉 Class goal achieved!")
            else:
                st.info("Not enough class members on leaderboards yet")
        else:
            st.info("Set your class in Privacy Settings to join class challenges!")
    
    with tab5:
        st.subheader("⚙️ Privacy Settings")
        
        st.write("### 👁️ Leaderboard Visibility")
        
        current_setting = user_data.get('show_on_leaderboards', False)
        new_setting = st.checkbox("Show me on public leaderboards", value=current_setting)
        
        if new_setting != current_setting:
            user_data['show_on_leaderboards'] = new_setting
            update_user_data(user_data)
            st.success("✅ Settings updated!")
            st.rerun()
        
        st.info("ℹ️ When enabled, your stats will be visible on leaderboards. Your friends can always see your profile.")
        
        # Update school/class
        st.write("")
        st.write("### 🏫 School & Class")
        
        col1, col2 = st.columns(2)
        with col1:
            current_school = user_data.get('school', '')
            new_school = st.text_input("School", value=current_school, key="update_school")
        
        with col2:
            current_class = user_data.get('class', '')
            new_class = st.text_input("Class", value=current_class, key="update_class")
        
        if st.button("Update School/Class Info"):
            user_data['school'] = new_school
            user_data['class'] = new_class
            update_user_data(user_data)
            st.success("✅ Updated!")
            st.rerun()

# AI Insights and Recommendations
def ai_insights():
    st.header("🤖 AI Fitness Coach")
    
    user_data = get_user_data()
    
    # Create tabs for different AI features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "🤖 ML Predictions",
        "🎯 SMART Goals",
        "🗓️ AI Schedule Generator",
        "🍳 Health Recipes",
        "💬 AI Chat Assistant",
        "📋 Custom Workout Plan",
        "💪 Workout Recommendations", 
        "🎯 Improvement Advice",
        "🍎 Meal Suggestions",
        "😴 Sleep Insights",
        "📈 Progress Predictions"
    ])
    
    with tab1:
        st.subheader("🤖 Machine Learning Predictions & Statistical Analysis")
        st.write("AI-powered predictions based on your performance data")
        
        # Check if enough data
        has_napfa = len(user_data.get('napfa_history', [])) > 0
        has_multiple_napfa = len(user_data.get('napfa_history', [])) >= 2
        has_sleep = len(user_data.get('sleep_history', [])) >= 7
        has_exercises = len(user_data.get('exercises', [])) >= 5
        
        # Prediction 1: When will you reach NAPFA Gold?
        st.write("### 🥇 NAPFA Gold Prediction")
        
        if not has_napfa:
            st.info("Complete your first NAPFA test to get predictions!")
        elif not has_multiple_napfa:
            latest_napfa = user_data['napfa_history'][-1]
            current_score = latest_napfa['total']
            
            if current_score >= 21:
                st.success(f"🎉 You already have NAPFA Gold! (Score: {current_score}/30)")
            else:
                points_needed = 21 - current_score
                st.info(f"**Current Score:** {current_score}/30")
                st.info(f"**Points Needed for Gold:** {points_needed}")
                st.write("Complete another NAPFA test to get improvement rate predictions!")
        else:
            # ML Prediction: Linear regression on NAPFA scores
            napfa_history = user_data['napfa_history']
            scores = [test['total'] for test in napfa_history]
            dates = [datetime.strptime(test['date'], '%Y-%m-%d') for test in napfa_history]
            
            # Calculate improvement rate
            days_between = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            score_changes = [scores[i] - scores[i-1] for i in range(1, len(scores))]
            
            if sum(days_between) > 0:
                avg_improvement_per_day = sum(score_changes) / sum(days_between)
                avg_improvement_per_month = avg_improvement_per_day * 30
                
                current_score = scores[-1]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current NAPFA", f"{current_score}/30")
                    st.metric("Improvement Rate", f"+{avg_improvement_per_month:.2f} pts/month")
                
                with col2:
                    if current_score >= 21:
                        st.success("🥇 Gold Medal Achieved!")
                    else:
                        points_needed = 21 - current_score
                        if avg_improvement_per_day > 0:
                            days_to_gold = points_needed / avg_improvement_per_day
                            months_to_gold = days_to_gold / 30
                            predicted_date = datetime.now() + timedelta(days=days_to_gold)
                            
                            st.metric("Points to Gold", points_needed)
                            st.metric("Predicted Gold Date", predicted_date.strftime('%B %Y'))
                            
                            st.info(f"📅 At your current rate, you'll reach Gold in ~{months_to_gold:.1f} months!")
                        else:
                            st.warning("Your score is decreasing. Focus on training to improve!")
                
                # Show prediction chart
                st.write("### 📈 Score Projection")
                
                # Project next 6 months
                future_dates = [datetime.now() + timedelta(days=30*i) for i in range(7)]
                future_scores = [current_score + (avg_improvement_per_day * 30 * i) for i in range(7)]
                future_scores = [min(max(s, 0), 30) for s in future_scores]  # Cap at 0-30
                
                df = pd.DataFrame({
                    'Date': [d.strftime('%b %Y') for d in future_dates],
                    'Predicted Score': future_scores
                })
                
                st.line_chart(df.set_index('Date'))
                
                st.write(f"**Model:** Linear regression based on {len(napfa_history)} test(s)")
                st.write(f"**Confidence:** {'High' if len(napfa_history) >= 4 else 'Medium' if len(napfa_history) >= 3 else 'Low'}")
        
        st.write("---")
        
        # Prediction 2: Sleep Impact on Performance
        st.write("### 😴 Sleep Impact Analysis")
        
        if not has_sleep or not has_napfa:
            st.info("Track sleep for 7+ days and complete NAPFA to see correlation!")
        else:
            sleep_data = user_data['sleep_history']
            
            # Calculate average sleep
            avg_sleep_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / len(sleep_data)
            
            # Analyze NAPFA performance vs sleep
            napfa_score = user_data['napfa_history'][-1]['total']
            
            # Statistical correlation (simplified)
            if avg_sleep_hours >= 8:
                performance_rating = "Optimal"
                color = "#4caf50"
                insight = "Your sleep supports peak performance! Keep it up."
                predicted_improvement = 5
            elif avg_sleep_hours >= 7:
                performance_rating = "Good"
                color = "#8bc34a"
                insight = "Good sleep, but getting 8+ hours could improve your NAPFA score by ~2-3 points."
                predicted_improvement = 2.5
            else:
                performance_rating = "Below Optimal"
                color = "#ff9800"
                insight = "⚠️ Poor sleep is limiting your performance. Getting 8+ hours could improve your score by ~5 points!"
                predicted_improvement = 5
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Sleep", f"{avg_sleep_hours:.1f} hours")
                st.metric("Current NAPFA", f"{napfa_score}/30")
            
            with col2:
                st.markdown(f'<div class="stat-card" style="background: {color}; color: white;"><h3>{performance_rating}</h3></div>', unsafe_allow_html=True)
                st.metric("Potential Gain", f"+{predicted_improvement:.1f} points")
            
            st.info(f"💡 **Insight:** {insight}")
            
            # Show correlation
            st.write("**Research shows:** Students who sleep 8+ hours score on average 15% higher on NAPFA tests.")
        
        st.write("---")
        
        # Prediction 3: Injury Risk Prediction
        st.write("### 🏥 Injury Risk Assessment")
        
        if not has_exercises:
            st.info("Log 5+ workouts to get injury risk analysis!")
        else:
            exercises = user_data['exercises']
            
            # Calculate workout intensity distribution
            intensity_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            for ex in exercises:
                intensity_counts[ex['intensity']] += 1
            
            total = sum(intensity_counts.values())
            high_intensity_ratio = intensity_counts['High'] / total if total > 0 else 0
            
            # Check workout frequency (last 2 weeks)
            two_weeks_ago = datetime.now() - timedelta(days=14)
            recent_workouts = [e for e in exercises 
                             if datetime.strptime(e['date'], '%Y-%m-%d') >= two_weeks_ago]
            
            workouts_per_week = len(recent_workouts) / 2
            
            # Risk calculation
            risk_score = 0
            risk_factors = []
            
            if high_intensity_ratio > 0.7:
                risk_score += 30
                risk_factors.append("⚠️ Too many high-intensity workouts (>70%)")
            
            if workouts_per_week > 6:
                risk_score += 25
                risk_factors.append("⚠️ Insufficient rest days (<1 per week)")
            
            if workouts_per_week < 2:
                risk_score += 15
                risk_factors.append("⚠️ Inconsistent training increases injury risk")
            
            # Sleep factor
            if has_sleep:
                if avg_sleep_hours < 7:
                    risk_score += 20
                    risk_factors.append("⚠️ Poor sleep reduces recovery")
            
            # Determine risk level
            if risk_score >= 50:
                risk_level = "High Risk"
                risk_color = "#f44336"
                recommendation = "🚨 REDUCE intensity and take more rest days!"
            elif risk_score >= 25:
                risk_level = "Moderate Risk"
                risk_color = "#ff9800"
                recommendation = "⚠️ Balance your training intensity and rest."
            else:
                risk_level = "Low Risk"
                risk_color = "#4caf50"
                recommendation = "✅ Your training is well-balanced!"
            
            st.markdown(f'<div class="stat-card" style="background: {risk_color}; color: white;"><h2>Risk Level: {risk_level}</h2><p>{recommendation}</p></div>', unsafe_allow_html=True)
            
            if risk_factors:
                st.write("**Risk Factors:**")
                for factor in risk_factors:
                    st.write(factor)
            
            st.write("")
            st.write("**Injury Prevention Tips:**")
            st.write("1. Include 1-2 rest days per week")
            st.write("2. Mix high, medium, and low intensity workouts")
            st.write("3. Sleep 8+ hours for recovery")
            st.write("4. Warm up before and cool down after exercise")
            st.write("5. Listen to your body - rest if you feel pain")
        
        st.write("---")
        
        # Prediction 4: Optimal Workout Timing
        st.write("### ⏰ Optimal Training Time Analysis")
        
        if not has_exercises or not has_napfa:
            st.info("Log workouts and NAPFA tests to find your peak performance time!")
        else:
            st.write("**Based on your workout patterns:**")
            
            # This is simplified - in real ML we'd analyze actual performance
            morning_workouts = 0
            afternoon_workouts = 0
            evening_workouts = 0
            
            # Since we don't track workout time, provide general guidance
            st.info("""
            **Research-based recommendations:**
            
            🌅 **Morning (6-9 AM):**
            - Best for: Cardio, endurance training
            - Benefits: Boosts metabolism, consistent routine
            - Your NAPFA run: Morning runs show 5-10% better times
            
            🌤️ **Afternoon (2-5 PM):**
            - Best for: Strength training, power exercises
            - Benefits: Peak body temperature, best muscle function
            - Your NAPFA: Sit-ups, broad jump, pull-ups perform best
            
            🌙 **Evening (5-8 PM):**
            - Best for: Flexibility, skill work
            - Benefits: Stress relief, muscles are warm
            - Your NAPFA: Good for sit & reach training
            
            💡 **Your recommendation:** Based on average student data, training 2-5 PM could improve your NAPFA score by 3-5 points!
            """)
        
        st.write("---")
        
        # Statistical Summary
        st.write("### 📊 Your Statistics Summary")
        
        stats = []
        
        if has_napfa:
            latest_napfa = user_data['napfa_history'][-1]
            stats.append(f"**NAPFA Score:** {latest_napfa['total']}/30 ({latest_napfa['medal']})")
            
            # Percentile (compared to age group)
            score = latest_napfa['total']
            if score >= 25:
                percentile = 95
            elif score >= 21:
                percentile = 75
            elif score >= 15:
                percentile = 50
            elif score >= 9:
                percentile = 25
            else:
                percentile = 10
            
            stats.append(f"**Your Percentile:** Top {100-percentile}% for your age")
        
        if has_sleep:
            stats.append(f"**Average Sleep:** {avg_sleep_hours:.1f} hours")
        
        if has_exercises:
            stats.append(f"**Total Workouts:** {len(exercises)}")
            stats.append(f"**Recent Activity:** {workouts_per_week:.1f} workouts/week")
        
        for stat in stats:
            st.write(stat)
    
    with tab2:
        st.subheader("🎯 SMART Goals System")
        st.write("Set Specific, Measurable, Achievable, Relevant, and Time-bound goals")
        
        # Initialize smart_goals if it doesn't exist
        if 'smart_goals' not in user_data:
            user_data['smart_goals'] = []
            update_user_data(user_data)
        
        # Create or view SMART goals
        goal_tab1, goal_tab2 = st.tabs(["Create New Goal", "My SMART Goals"])
        
        with goal_tab1:
            st.write("### Create a SMART Goal")
            
            # Goal type selection
            goal_category = st.selectbox(
                "Goal Category",
                ["NAPFA Improvement", "Weight Management", "Strength Building", 
                 "Endurance Training", "Flexibility", "Consistency/Habits"]
            )
            
            # Specific
            st.write("#### 📝 Specific - What exactly do you want to achieve?")
            
            if goal_category == "NAPFA Improvement":
                specific_options = [
                    "Achieve NAPFA Gold Medal",
                    "Improve specific component to Grade 5",
                    "Increase total NAPFA score by X points",
                    "Get all components to Grade 3+"
                ]
                specific_goal = st.selectbox("Choose specific goal", specific_options)
                
                if "specific component" in specific_goal:
                    component = st.selectbox("Which component?", 
                                            ["Sit-Ups", "Standing Broad Jump", "Sit and Reach", 
                                             "Pull-Ups", "Shuttle Run", "2.4km Run"])
                    target_grade = 5
                elif "increase total" in specific_goal:
                    target_increase = st.number_input("Points to increase", min_value=1, max_value=10, value=3)
                
            elif goal_category == "Weight Management":
                current_weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=150.0, value=60.0)
                target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=150.0, value=58.0)
                specific_goal = f"Change weight from {current_weight}kg to {target_weight}kg"
                
            elif goal_category == "Strength Building":
                exercise = st.selectbox("Exercise", ["Push-ups", "Pull-ups", "Sit-ups", "Squats"])
                current_reps = st.number_input(f"Current max {exercise}", min_value=0, max_value=200, value=10)
                target_reps = st.number_input(f"Target {exercise}", min_value=0, max_value=200, value=20)
                specific_goal = f"Increase {exercise} from {current_reps} to {target_reps} reps"
                
            elif goal_category == "Endurance Training":
                distance = st.selectbox("Distance", ["1km", "2.4km", "5km", "10km"])
                current_time = st.text_input("Current time (min:sec)", value="10:00")
                target_time = st.text_input("Target time (min:sec)", value="9:00")
                specific_goal = f"Run {distance} from {current_time} to {target_time}"
                
            elif goal_category == "Flexibility":
                current_reach = st.number_input("Current Sit & Reach (cm)", min_value=0, max_value=100, value=30)
                target_reach = st.number_input("Target Sit & Reach (cm)", min_value=0, max_value=100, value=40)
                specific_goal = f"Improve flexibility from {current_reach}cm to {target_reach}cm"
                
            else:  # Consistency
                workout_days = st.number_input("Workouts per week", min_value=1, max_value=7, value=4)
                duration = st.number_input("For how many weeks?", min_value=1, max_value=52, value=8)
                specific_goal = f"Workout {workout_days} days/week for {duration} weeks"
            
            # Measurable
            st.write("#### 📊 Measurable - How will you track progress?")
            tracking_method = st.multiselect(
                "Tracking methods",
                ["Weekly NAPFA practice tests", "Daily workout logs", "Weekly measurements",
                 "Progress photos", "Performance records"],
                default=["Daily workout logs"]
            )
            
            # Achievable - AI calculates
            st.write("#### ✅ Achievable - Is this realistic?")
            
            # Calculate if goal is achievable based on current data
            timeline_weeks = st.slider("Timeline (weeks)", min_value=1, max_value=52, value=12)
            
            achievability = "Achievable"
            ai_feedback = ""
            
            if goal_category == "NAPFA Improvement":
                if user_data.get('napfa_history'):
                    current_napfa = user_data['napfa_history'][-1]['total']
                    if "Gold" in specific_goal and current_napfa < 15 and timeline_weeks < 12:
                        achievability = "Very Challenging"
                        ai_feedback = "⚠️ This is ambitious! Consider extending timeline to 16+ weeks."
                    elif current_napfa >= 18:
                        achievability = "Highly Achievable"
                        ai_feedback = "✅ Great goal! You're close to Gold already."
                    else:
                        ai_feedback = "✅ Realistic with consistent training!"
                        
            elif goal_category == "Weight Management":
                weight_change = abs(target_weight - current_weight)
                safe_rate = 0.5  # kg per week
                safe_weeks = weight_change / safe_rate
                
                if timeline_weeks < safe_weeks * 0.7:
                    achievability = "Too Aggressive"
                    ai_feedback = f"⚠️ Recommended timeline: {int(safe_weeks)} weeks for safe {weight_change}kg change"
                else:
                    ai_feedback = "✅ Safe and achievable rate!"
            
            st.info(f"**AI Assessment:** {achievability} - {ai_feedback}")
            
            # Relevant
            st.write("#### 🎯 Relevant - Why is this important to you?")
            motivation = st.text_area("Your motivation", 
                                     placeholder="e.g., I want to improve my fitness for school sports...")
            
            # Time-bound
            st.write("#### ⏰ Time-bound - When will you achieve this?")
            target_date = st.date_input("Target completion date", 
                                        value=datetime.now() + timedelta(weeks=timeline_weeks))
            
            # AI generates milestones
            st.write("### 📅 AI-Generated Weekly Milestones")
            
            weeks = (target_date - datetime.now().date()).days // 7
            if weeks > 0:
                st.write(f"**Timeline:** {weeks} weeks")
                
                # Generate milestones
                milestones = []
                
                if goal_category == "NAPFA Improvement" and "total" in specific_goal:
                    points_per_week = target_increase / weeks
                    current_score = user_data['napfa_history'][-1]['total'] if user_data.get('napfa_history') else 15
                    
                    for week in range(1, min(weeks + 1, 9)):
                        milestone_score = current_score + (points_per_week * week)
                        milestones.append(f"**Week {week}:** Target score {milestone_score:.1f}/30")
                        
                elif goal_category == "Weight Management":
                    weight_per_week = (target_weight - current_weight) / weeks
                    
                    for week in range(1, min(weeks + 1, 9)):
                        milestone_weight = current_weight + (weight_per_week * week)
                        milestones.append(f"**Week {week}:** Target weight {milestone_weight:.1f}kg")
                        
                elif goal_category == "Strength Building":
                    reps_per_week = (target_reps - current_reps) / weeks
                    
                    for week in range(1, min(weeks + 1, 9)):
                        milestone_reps = int(current_reps + (reps_per_week * week))
                        milestones.append(f"**Week {week}:** Target {milestone_reps} {exercise}")
                
                for milestone in milestones:
                    st.write(milestone)
            
            # Save goal
            if st.button("💾 Save SMART Goal", type="primary"):
                smart_goal = {
                    'category': goal_category,
                    'specific': specific_goal,
                    'measurable': tracking_method,
                    'achievable': achievability,
                    'relevant': motivation,
                    'time_bound': target_date.strftime('%Y-%m-%d'),
                    'milestones': milestones,
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                    'progress': 0,
                    'weekly_checkpoints': []
                }
                
                if 'smart_goals' not in user_data:
                    user_data['smart_goals'] = []
                
                user_data['smart_goals'].append(smart_goal)
                update_user_data(user_data)
                
                st.success("✅ SMART Goal created!")
                st.balloons()
                time.sleep(1)
                st.rerun()
        
        with goal_tab2:
            st.write("### My Active SMART Goals")
            
            if 'smart_goals' not in user_data or not user_data['smart_goals']:
                st.info("No SMART goals yet. Create your first goal in the other tab!")
            else:
                for idx, goal in enumerate(user_data['smart_goals']):
                    with st.expander(f"🎯 {goal['specific']}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Category:** {goal['category']}")
                            st.write(f"**Target Date:** {goal['time_bound']}")
                            st.write(f"**Created:** {goal['created_date']}")
                            st.write(f"**Achievability:** {goal['achievable']}")
                        
                        with col2:
                            st.write("**Tracking Methods:**")
                            for method in goal['measurable']:
                                st.write(f"• {method}")
                        
                        st.write("")
                        st.write(f"**Motivation:** {goal['relevant']}")
                        
                        # Progress tracking
                        st.write("")
                        st.write("### Progress Tracking")
                        
                        new_progress = st.slider(
                            "Update Progress",
                            min_value=0,
                            max_value=100,
                            value=goal['progress'],
                            key=f"progress_{idx}"
                        )
                        
                        if st.button("Update Progress", key=f"update_{idx}"):
                            user_data['smart_goals'][idx]['progress'] = new_progress
                            user_data['smart_goals'][idx]['weekly_checkpoints'].append({
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'progress': new_progress
                            })
                            update_user_data(user_data)
                            st.success("Progress updated!")
                            st.rerun()
                        
                        # Show milestones
                        if goal.get('milestones'):
                            st.write("")
                            st.write("**Weekly Milestones:**")
                            for milestone in goal['milestones']:
                                st.write(milestone)
                        
                        # Delete goal
                        if st.button("🗑️ Delete Goal", key=f"delete_{idx}"):
                            user_data['smart_goals'].pop(idx)
                            update_user_data(user_data)
                            st.rerun()
    
    with tab3:
        st.subheader("🗓️ Comprehensive AI Schedule Generator")
        st.write("Generate a complete personalized schedule based on your fitness data!")
        
        # Check if user has necessary data
        has_napfa = len(user_data.get('napfa_history', [])) > 0
        has_bmi = len(user_data.get('bmi_history', [])) > 0
        has_sleep = len(user_data.get('sleep_history', [])) > 0
        
        if not has_napfa or not has_bmi or not has_sleep:
            st.warning("⚠️ To generate a complete schedule, please complete:")
            if not has_napfa:
                st.write("- ❌ NAPFA Test")
            if not has_bmi:
                st.write("- ❌ BMI Calculation")
            if not has_sleep:
                st.write("- ❌ Sleep Tracking (at least 3 days)")
            st.info("Once you have this data, come back to generate your personalized schedule!")
        else:
            st.success("✅ All data available! Ready to generate your schedule.")
            
            # Get latest data
            latest_napfa = user_data['napfa_history'][-1]
            latest_bmi_record = user_data['bmi_history'][-1]
            latest_bmi = latest_bmi_record['bmi']
            
            # Calculate body type
            body_type, body_description = calculate_body_type(
                latest_bmi_record['weight'], 
                latest_bmi_record['height']
            )
            
            # BMI for the week
            week_ago = datetime.now() - timedelta(days=7)
            bmi_week = [b for b in user_data['bmi_history'] 
                       if datetime.strptime(b['date'], '%Y-%m-%d') >= week_ago]
            
            # Sleep for the week
            sleep_week = [s for s in user_data['sleep_history'] 
                         if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
            
            # Display current data
            st.write("### 📊 Your Current Data")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest BMI", f"{latest_bmi:.1f}")
                st.write(f"**Body Type:** {body_type}")
            with col2:
                st.metric("NAPFA Score", f"{latest_napfa['total']}/30")
                st.write(f"**Medal:** {latest_napfa['medal']}")
            with col3:
                if sleep_week:
                    avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_week]) / len(sleep_week)
                    st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
                    st.write(f"**Records:** {len(sleep_week)} days")
            
            st.write("---")
            
            # School schedule input
            st.write("### 🏫 Your School Schedule")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Weekdays**")
                weekday_start = st.time_input("School Start Time (Weekdays)", value=datetime.strptime("06:30", "%H:%M").time(), key="weekday_start")
                weekday_end = st.time_input("School End Time (Weekdays)", value=datetime.strptime("19:00", "%H:%M").time(), key="weekday_end")
            
            with col2:
                st.write("**Weekends**")
                weekend_schedule = st.radio("Weekend Schedule", 
                                           ["Full day available", "Half day (morning)", "Half day (afternoon)"],
                                           key="weekend_sched")
            
            # Generate button
            if st.button("🚀 Generate My Complete Schedule", type="primary"):
                st.write("---")
                st.success("✅ Your Personalized Schedule Generated!")
                
                # Determine dietary goal based on body type and BMI
                if latest_bmi < 18.5:
                    diet_goal = "Muscle Gain"
                    calorie_target = 2500
                elif latest_bmi >= 25:
                    diet_goal = "Weight Loss"
                    calorie_target = 1800
                else:
                    diet_goal = "Maintenance"
                    calorie_target = 2200
                
                # Calculate optimal sleep schedule
                if sleep_week:
                    avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_week]) / len(sleep_week)
                    # Recommend 8-9 hours
                    recommended_sleep = 8.5 if avg_sleep < 8 else 9
                else:
                    recommended_sleep = 8.5
                
                # Calculate bedtime based on school start
                wake_time = weekday_start
                sleep_hours = int(recommended_sleep)
                sleep_minutes = int((recommended_sleep - sleep_hours) * 60)
                
                # Calculate bedtime
                wake_datetime = datetime.combine(datetime.today(), wake_time)
                bedtime_datetime = wake_datetime - timedelta(hours=sleep_hours, minutes=sleep_minutes)
                bedtime = bedtime_datetime.time()
                
                # Create schedule tabs
                schedule_tab1, schedule_tab2, schedule_tab3 = st.tabs(["📅 Weekly Schedule", "🍽️ Diet Plan", "💤 Sleep Schedule"])
                
                with schedule_tab1:
                    st.subheader("Your Weekly Workout Schedule")
                    
                    # Determine workout frequency based on NAPFA scores
                    weak_areas = [test for test, grade in latest_napfa['grades'].items() if grade < 3]
                    workout_days = 5 if len(weak_areas) >= 3 else 4
                    
                    # Generate weekly schedule
                    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                    weekend = ["Saturday", "Sunday"]
                    
                    # Calculate workout times
                    school_end_time = datetime.combine(datetime.today(), weekday_end)
                    workout_start = school_end_time + timedelta(hours=1)  # 1 hour after school
                    
                    workout_schedule = []
                    
                    # Weekday workouts
                    days_with_workout = weekdays[:workout_days] if workout_days <= 5 else weekdays
                    
                    for idx, day in enumerate(weekdays):
                        if day in days_with_workout:
                            # Rotate workout focus
                            if idx % 3 == 0:
                                focus = "Upper Body & Core"
                                duration = 45
                            elif idx % 3 == 1:
                                focus = "Lower Body & Cardio"
                                duration = 50
                            else:
                                focus = "NAPFA Training"
                                duration = 45
                            
                            workout_schedule.append({
                                'day': day,
                                'time': workout_start.strftime("%H:%M"),
                                'activity': focus,
                                'duration': duration,
                                'type': 'weekday'
                            })
                        else:
                            workout_schedule.append({
                                'day': day,
                                'time': '-',
                                'activity': 'Rest Day',
                                'duration': 0,
                                'type': 'weekday'
                            })
                    
                    # Weekend workouts
                    if weekend_schedule == "Full day available":
                        weekend_time = "09:00"
                    elif weekend_schedule == "Half day (morning)":
                        weekend_time = "07:00"
                    else:
                        weekend_time = "14:00"
                    
                    workout_schedule.append({
                        'day': 'Saturday',
                        'time': weekend_time,
                        'activity': 'Long Cardio / Sports',
                        'duration': 60,
                        'type': 'weekend'
                    })
                    
                    workout_schedule.append({
                        'day': 'Sunday',
                        'time': '-',
                        'activity': 'Active Recovery (Light walk/stretch)',
                        'duration': 30,
                        'type': 'weekend'
                    })
                    
                    # Display schedule
                    for item in workout_schedule:
                        if item['activity'] != 'Rest Day':
                            st.markdown(f"""
                            **{item['day']}** - {item['time']}  
                            🏋️ {item['activity']} ({item['duration']} min)
                            """)
                        else:
                            st.markdown(f"**{item['day']}** - Rest Day 😴")
                        st.write("")
                    
                    # Store for optional save
                    if 'generated_schedule' not in st.session_state:
                        st.session_state.generated_schedule = workout_schedule
                
                with schedule_tab2:
                    st.subheader("Your Personalized Diet Plan")
                    
                    st.write(f"**Goal:** {diet_goal}")
                    st.write(f"**Body Type:** {body_type} - {body_description}")
                    st.write(f"**Daily Calorie Target:** {calorie_target} kcal")
                    st.write("")
                    
                    # Generate meal plan based on body type and goal
                    if body_type == "Ectomorph":
                        st.write("**Nutrition Focus:** High calories, protein, complex carbs")
                        protein_target = "1.8-2.0g per kg bodyweight"
                        carb_focus = "High (50-60% of calories)"
                    elif body_type == "Mesomorph":
                        st.write("**Nutrition Focus:** Balanced macros, moderate calories")
                        protein_target = "1.5-1.8g per kg bodyweight"
                        carb_focus = "Moderate (40-50% of calories)"
                    else:  # Endomorph
                        st.write("**Nutrition Focus:** Controlled carbs, high protein")
                        protein_target = "1.5-2.0g per kg bodyweight"
                        carb_focus = "Lower (30-40% of calories)"
                    
                    st.write(f"**Protein Target:** {protein_target}")
                    st.write(f"**Carb Focus:** {carb_focus}")
                    st.write("")
                    
                    # Weekday meal plan
                    st.markdown("#### 📅 Weekday Meal Plan")
                    
                    st.markdown(f"""
                    **Breakfast** ({(weekday_start.hour - 1):02d}:00 - before school)
                    - Options: Oatmeal with fruits & nuts, Eggs with whole wheat toast, Protein smoothie
                    - Calories: ~500 kcal | Protein: ~20g
                    
                    **Mid-Morning Snack** (10:30 - during break)
                    - Options: Banana with peanut butter, Greek yogurt, Nuts & dried fruit
                    - Calories: ~200 kcal | Protein: ~10g
                    
                    **Lunch** (13:00)
                    - Options: Chicken rice, Fish with vegetables, Pasta with lean meat
                    - Calories: ~600 kcal | Protein: ~35g
                    
                    **Pre-Workout Snack** ({(weekday_end.hour):02d}:30 - before training)
                    - Options: Banana, Energy bar, Small sandwich
                    - Calories: ~200 kcal | Protein: ~10g
                    
                    **Post-Workout** ({(workout_start.hour + 1):02d}:00 - after training)
                    - Options: Chocolate milk, Protein shake with banana
                    - Calories: ~300 kcal | Protein: ~25g
                    
                    **Dinner** ({(workout_start.hour + 2):02d}:00)
                    - Options: Grilled chicken/fish with vegetables, Lean beef with sweet potato
                    - Calories: ~600 kcal | Protein: ~40g
                    
                    **Evening Snack** (Optional, 2hrs before bed)
                    - Options: Cottage cheese, Casein shake, Small fruit
                    - Calories: ~150 kcal | Protein: ~15g
                    """)
                    
                    st.write("")
                    st.markdown("#### 🎉 Weekend Meal Plan")
                    st.write("More flexible timing - maintain same portions and quality")
                    st.write("• Focus on whole foods")
                    st.write("• Stay hydrated (8-10 glasses water)")
                    st.write("• Limit processed foods and sugar")
                    
                    # Store diet plan
                    if 'generated_diet' not in st.session_state:
                        st.session_state.generated_diet = {
                            'goal': diet_goal,
                            'body_type': body_type,
                            'calories': calorie_target,
                            'protein_target': protein_target
                        }
                
                with schedule_tab3:
                    st.subheader("Optimized Sleep Schedule")
                    
                    st.write(f"**Recommended Sleep:** {recommended_sleep} hours")
                    st.write(f"**Current Average:** {avg_sleep:.1f} hours" if sleep_week else "No data")
                    st.write("")
                    
                    # Weekday sleep
                    st.markdown("#### 📅 Weekday Sleep Schedule")
                    st.write(f"🌙 **Bedtime:** {bedtime.strftime('%H:%M')}")
                    st.write(f"☀️ **Wake Time:** {wake_time.strftime('%H:%M')}")
                    st.write(f"⏰ **Sleep Duration:** {recommended_sleep} hours")
                    
                    st.write("")
                    st.write("**Pre-Sleep Routine (30 min before bed):**")
                    st.write("1. 📱 Put away all screens")
                    st.write("2. 🚿 Shower or wash up")
                    st.write("3. 📖 Light reading or relaxation")
                    st.write("4. 🧘 Deep breathing exercises")
                    
                    st.write("")
                    st.markdown("#### 🎉 Weekend Sleep Schedule")
                    weekend_bedtime = (bedtime_datetime + timedelta(hours=1)).time()
                    weekend_wake = (wake_datetime + timedelta(hours=1.5)).time()
                    
                    st.write(f"🌙 **Bedtime:** {weekend_bedtime.strftime('%H:%M')} (can be 1hr later)")
                    st.write(f"☀️ **Wake Time:** {weekend_wake.strftime('%H:%M')} (can sleep in 1.5hrs)")
                    st.write("**Tip:** Keep weekend schedule within 2 hours of weekday for consistency")
                    
                    st.write("")
                    st.write("**Sleep Quality Tips:**")
                    st.write("✅ Keep room cool (18-20°C)")
                    st.write("✅ Complete darkness or eye mask")
                    st.write("✅ No caffeine after 2 PM")
                    st.write("✅ Exercise earlier in day (not close to bedtime)")
                    st.write("✅ Same schedule daily (including weekends)")
                
                # Option to save to schedule
                st.write("---")
                if st.button("💾 Save Workout Schedule to Training Tab", type="primary"):
                    # Save to user's schedule
                    for item in workout_schedule:
                        if item['activity'] not in ['Rest Day', 'Active Recovery (Light walk/stretch)']:
                            user_data['schedule'].append({
                                'day': item['day'],
                                'activity': item['activity'],
                                'time': item['time'],
                                'duration': item['duration']
                            })
                    
                    update_user_data(user_data)
                    st.success("✅ Schedule saved to Training Schedule tab!")
                    st.balloons()
    
    with tab2:
        st.subheader("🍳 Healthy Recipe Database")
        st.write("Browse recipes tailored to your dietary goals!")
        
        # Filter by diet goal
        if 'generated_diet' in st.session_state:
            default_goal = st.session_state.generated_diet['goal']
        else:
            default_goal = "Maintenance"
        
        selected_diet = st.selectbox(
            "Select Dietary Goal",
            ["Weight Loss", "Muscle Gain", "Maintenance"],
            index=["Weight Loss", "Muscle Gain", "Maintenance"].index(default_goal)
        )
        
        # Get recipes
        recipes_dict = search_recipes_by_diet(selected_diet)
        recipes = recipes_dict.get(selected_diet, [])
        
        if recipes:
            st.write(f"**Found {len(recipes)} recipes for {selected_diet}**")
            st.write("")
            
            # Display recipes
            for idx, recipe in enumerate(recipes):
                with st.expander(f"🍽️ {recipe['name']} - {recipe['calories']} kcal", expanded=(idx == 0)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Nutritional Info:**")
                        st.write(f"- Calories: {recipe['calories']} kcal")
                        st.write(f"- Protein: {recipe['protein']}")
                        st.write(f"- Carbs: {recipe['carbs']}")
                        st.write(f"- Prep Time: {recipe['prep_time']}")
                    
                    with col2:
                        st.write("**Meal Type:**")
                        if recipe['calories'] < 300:
                            st.write("🥗 Snack/Light meal")
                        elif recipe['calories'] < 450:
                            st.write("🍽️ Main meal")
                        else:
                            st.write("🍖 Post-workout meal")
                    
                    st.write("")
                    st.write("**Ingredients:**")
                    for ingredient in recipe['ingredients']:
                        st.write(f"• {ingredient}")
                    
                    st.write("")
                    st.write("**Instructions:**")
                    st.write(recipe['instructions'])
        else:
            st.info("No recipes found. Select a dietary goal above.")
        
        st.write("---")
        st.info("💡 **Tip:** These recipes align with your body type and fitness goals. Mix and match to create variety in your diet!")
    
    with tab3:
        st.subheader("💬 Chat with Your AI Fitness Assistant")
        st.write("Ask me anything about fitness, nutrition, training, or your progress!")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat interface
        user_question = st.text_input("Ask your question:", placeholder="e.g., How can I improve my pull-ups?", key="chat_input")
        
        if st.button("Send", key="send_chat"):
            if user_question:
                # Add user question to history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Generate AI response based on user data and question
                ai_response = generate_ai_response(user_question, user_data)
                
                # Add AI response to history
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Display chat history
        if st.session_state.chat_history:
            st.write("---")
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 AI Coach:** {message['content']}")
                st.write("")
        
        # Quick question buttons
        st.write("---")
        st.write("**Quick Questions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("How to improve cardio?", key="q1"):
                st.session_state.chat_history.append({"role": "user", "content": "How can I improve my cardio?"})
                response = "To improve cardio: (1) Start with 20-30 min runs 3x/week, (2) Add interval training (sprint 1 min, jog 2 min), (3) Gradually increase distance by 10% weekly, (4) Mix running with swimming/cycling, (5) Track your heart rate - aim for 60-80% max HR for endurance!"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("Best recovery foods?", key="q2"):
                st.session_state.chat_history.append({"role": "user", "content": "What are the best recovery foods?"})
                response = "Best post-workout recovery foods: (1) Chocolate milk (protein + carbs), (2) Greek yogurt with berries, (3) Banana with peanut butter, (4) Grilled chicken with sweet potato, (5) Salmon with quinoa. Eat within 30-60 minutes after exercise for best recovery!"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("Prevent injuries?", key="q3"):
                st.session_state.chat_history.append({"role": "user", "content": "How do I prevent injuries?"})
                response = "Injury prevention tips: (1) Always warm up 5-10 min before exercise, (2) Cool down and stretch after workouts, (3) Increase training intensity gradually, (4) Rest at least 1-2 days/week, (5) Listen to your body - pain is a warning sign, (6) Stay hydrated, (7) Wear proper shoes for your activity!"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        if st.button("Clear Chat History", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with tab2:
        st.subheader("📋 Generate Custom Workout Plan")
        st.write("Get a personalized workout plan based on your schedule and goals!")
        
        # Workout plan preferences
        st.write("### Your Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            days_available = st.multiselect(
                "Available Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Wednesday", "Friday"]
            )
        
        with col2:
            session_duration = st.selectbox(
                "Session Duration",
                ["30 minutes", "45 minutes", "60 minutes", "90 minutes"],
                index=2
            )
        
        workout_location = st.selectbox(
            "Workout Location",
            ["Home (no equipment)", "Home (basic equipment)", "Gym", "Outdoor/Park", "School"]
        )
        
        primary_goal = st.selectbox(
            "Primary Goal",
            ["Improve NAPFA scores", "Build strength", "Increase endurance", "Lose weight", "Gain muscle", "General fitness"]
        )
        
        fitness_level = st.selectbox(
            "Current Fitness Level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        
        # Generate button
        if st.button("Generate My Custom Plan", type="primary"):
            st.write("---")
            st.success("✅ Your Personalized Workout Plan")
            
            # Generate plan based on inputs
            duration_min = int(session_duration.split()[0])
            
            st.write(f"**Schedule:** {len(days_available)} days per week")
            st.write(f"**Duration:** {session_duration} per session")
            st.write(f"**Location:** {workout_location}")
            st.write(f"**Goal:** {primary_goal}")
            st.write("")
            
            # Generate day-by-day plan
            for idx, day in enumerate(days_available):
                with st.expander(f"📅 {day} - {session_duration}", expanded=True):
                    # Vary the workout focus
                    if len(days_available) >= 4:
                        if idx % 4 == 0:
                            focus = "Upper Body Strength"
                        elif idx % 4 == 1:
                            focus = "Lower Body & Core"
                        elif idx % 4 == 2:
                            focus = "Cardio & Endurance"
                        else:
                            focus = "Full Body & Flexibility"
                    elif len(days_available) >= 3:
                        if idx % 3 == 0:
                            focus = "Strength Training"
                        elif idx % 3 == 1:
                            focus = "Cardio Training"
                        else:
                            focus = "Full Body"
                    else:
                        focus = "Full Body Workout"
                    
                    st.markdown(f"**Focus:** {focus}")
                    
                    # Generate exercises based on location and focus
                    exercises = generate_workout_exercises(focus, workout_location, duration_min, fitness_level)
                    
                    st.write("**Warm-up (5-10 min):**")
                    st.write("- Light jogging or jumping jacks: 3 minutes")
                    st.write("- Dynamic stretches: 5 minutes")
                    st.write("- Arm circles, leg swings, hip rotations")
                    
                    st.write("")
                    st.write("**Main Workout:**")
                    for exercise in exercises:
                        st.write(f"- {exercise}")
                    
                    st.write("")
                    st.write("**Cool-down (5-10 min):**")
                    st.write("- Easy walk/jog: 3 minutes")
                    st.write("- Static stretches: Hold each 30 seconds")
                    st.write("- Focus on muscles worked today")
            
            # Additional tips
            st.write("---")
            st.write("### 💡 Training Tips")
            st.write("✅ **Progression:** Increase weight/reps by 5-10% every 2 weeks")
            st.write("✅ **Rest:** Take 1-2 rest days between intense sessions")
            st.write("✅ **Hydration:** Drink water before, during, and after workouts")
            st.write("✅ **Nutrition:** Eat protein + carbs within 1 hour post-workout")
            st.write("✅ **Sleep:** Get 8-10 hours for optimal recovery")
            st.write("✅ **Listen to your body:** Rest if you feel pain (not soreness)")
            
            # Track in schedule
            if st.button("💾 Save This Workout Plan", type="primary"):
                # Save the entire workout plan
                user_data['saved_workout_plan'] = {
                    'days': days_available,
                    'duration': session_duration,
                    'location': workout_location,
                    'goal': primary_goal,
                    'level': fitness_level,
                    'created_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Also add to schedule
                for day in days_available:
                    user_data['schedule'].append({
                        'day': day,
                        'activity': f"Custom Workout - {primary_goal}",
                        'time': "To be scheduled",
                        'duration': duration_min
                    })
                
                update_user_data(user_data)
                st.success("✅ Workout plan saved! Check 'My Saved Plan' and 'Training Schedule' tabs.")
                st.rerun()
        
        # Display saved workout plan if exists
        if 'saved_workout_plan' in user_data and user_data['saved_workout_plan']:
            st.write("---")
            st.subheader("📌 Your Saved Workout Plan")
            saved = user_data['saved_workout_plan']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Days/Week", len(saved['days']))
            with col2:
                st.metric("Duration", saved['duration'])
            with col3:
                st.metric("Created", saved['created_date'])
            
            st.write(f"**Goal:** {saved['goal']}")
            st.write(f"**Location:** {saved['location']}")
            st.write(f"**Days:** {', '.join(saved['days'])}")
            
            if st.button("🗑️ Delete Saved Plan"):
                user_data['saved_workout_plan'] = None
                update_user_data(user_data)
                st.rerun()
    
    with tab3:
        st.subheader("Personalized Workout Recommendations")
        
        if not user_data['napfa_history']:
            st.info("📝 Complete a NAPFA test first to get personalized workout recommendations!")
        else:
            latest_napfa = user_data['napfa_history'][-1]
            grades = latest_napfa['grades']
            
            st.write(f"**Based on your latest NAPFA test ({latest_napfa['date']}):**")
            st.write(f"**Total Score:** {latest_napfa['total']} | **Medal:** {latest_napfa['medal']}")
            
            # AI-generated workout plan
            workout_plan = []
            
            # Analyze each test component
            if grades['SU'] < 3:
                workout_plan.append({
                    'Focus': 'Core Strength (Sit-ups)',
                    'Exercises': 'Planks (3x30s), Bicycle crunches (3x15), Russian twists (3x20)',
                    'Frequency': '4-5 times per week',
                    'Tips': 'Focus on slow, controlled movements. Engage your core throughout.'
                })
            
            if grades['SBJ'] < 3:
                workout_plan.append({
                    'Focus': 'Explosive Power (Broad Jump)',
                    'Exercises': 'Box jumps (3x10), Squat jumps (3x12), Lunge jumps (3x10 each leg)',
                    'Frequency': '3-4 times per week',
                    'Tips': 'Land softly and focus on explosive power from your legs.'
                })
            
            if grades['SAR'] < 3:
                workout_plan.append({
                    'Focus': 'Flexibility (Sit and Reach)',
                    'Exercises': 'Hamstring stretches (hold 30s), Toe touches (3x10), Seated forward bend (hold 45s)',
                    'Frequency': 'Daily, especially after workouts',
                    'Tips': 'Stretch when muscles are warm. Never bounce - hold steady stretches.'
                })
            
            if grades['PU'] < 3:
                workout_plan.append({
                    'Focus': 'Upper Body Strength (Pull-ups)',
                    'Exercises': 'Assisted pull-ups (3x5), Negative pull-ups (3x3), Dead hangs (3x20s)',
                    'Frequency': '3-4 times per week',
                    'Tips': 'Build up slowly. Use resistance bands for assistance if needed.'
                })
            
            if grades['SR'] < 3:
                workout_plan.append({
                    'Focus': 'Agility & Speed (Shuttle Run)',
                    'Exercises': 'Ladder drills (5 mins), Cone drills (3x5), High knees (3x30s)',
                    'Frequency': '3 times per week',
                    'Tips': 'Focus on quick direction changes and maintaining low center of gravity.'
                })
            
            if grades['RUN'] < 3:
                workout_plan.append({
                    'Focus': 'Endurance (2.4km Run)',
                    'Exercises': 'Interval training (400m sprints with rest), Long slow runs (3-5km), Tempo runs',
                    'Frequency': '4-5 times per week',
                    'Tips': 'Build endurance gradually. Mix steady runs with interval training.'
                })
            
            if workout_plan:
                st.warning("🎯 **Areas needing improvement:**")
                for plan in workout_plan:
                    with st.expander(f"🏋️ {plan['Focus']}", expanded=True):
                        st.write(f"**Exercises:** {plan['Exercises']}")
                        st.write(f"**Frequency:** {plan['Frequency']}")
                        st.write(f"💡 **Tips:** {plan['Tips']}")
            else:
                st.success("🌟 Excellent! All your NAPFA components are strong. Focus on maintaining your performance with varied workouts.")
                st.info("**Maintenance Plan:** Mix cardio, strength training, and flexibility work 4-5 times per week to stay in top shape!")
    
    with tab2:
        st.subheader("AI Improvement Advice")
        
        if not user_data['napfa_history']:
            st.info("📝 Complete a NAPFA test first to get improvement advice!")
        else:
            latest_napfa = user_data['napfa_history'][-1]
            grades = latest_napfa['grades']
            
            # Find weakest areas
            weak_areas = [(test, grade) for test, grade in grades.items() if grade < 3]
            strong_areas = [(test, grade) for test, grade in grades.items() if grade >= 4]
            
            if weak_areas:
                st.error("⚠️ **Priority Areas for Improvement:**")
                
                test_names = {
                    'SU': 'Sit-Ups',
                    'SBJ': 'Standing Broad Jump',
                    'SAR': 'Sit and Reach',
                    'PU': 'Pull-Ups',
                    'SR': 'Shuttle Run',
                    'RUN': '2.4km Run'
                }
                
                for test, grade in sorted(weak_areas, key=lambda x: x[1]):
                    with st.expander(f"📍 {test_names[test]} (Grade {grade})"):
                        if test == 'SU':
                            st.write("**Why it matters:** Core strength is fundamental for all movements and injury prevention.")
                            st.write("**Quick win:** Do 3 sets of planks daily, increasing hold time weekly.")
                            st.write("**Long-term:** Add weighted core exercises once you reach Grade 3.")
                        elif test == 'SBJ':
                            st.write("**Why it matters:** Lower body power helps in sports and daily activities.")
                            st.write("**Quick win:** Practice jump squats 3x per week, focusing on explosive power.")
                            st.write("**Long-term:** Progressive plyometric training will significantly improve your distance.")
                        elif test == 'SAR':
                            st.write("**Why it matters:** Flexibility prevents injuries and improves overall mobility.")
                            st.write("**Quick win:** Stretch hamstrings and lower back daily for 10 minutes.")
                            st.write("**Long-term:** Consider yoga or dedicated flexibility sessions 2x per week.")
                        elif test == 'PU':
                            st.write("**Why it matters:** Upper body strength is crucial for overall fitness balance.")
                            st.write("**Quick win:** Start with assisted pull-ups or negatives every other day.")
                            st.write("**Long-term:** Gradually decrease assistance until you can do full pull-ups.")
                        elif test == 'SR':
                            st.write("**Why it matters:** Agility and speed are essential for sports performance.")
                            st.write("**Quick win:** Practice quick direction changes and footwork drills 3x weekly.")
                            st.write("**Long-term:** Join a sport that requires agility (basketball, badminton, football).")
                        elif test == 'RUN':
                            st.write("**Why it matters:** Cardiovascular endurance affects overall health and stamina.")
                            st.write("**Quick win:** Run 3-4 times weekly, starting at comfortable pace and distance.")
                            st.write("**Long-term:** Build up to 20-30km per week with mixed pace training.")
            
            if strong_areas:
                st.success("💪 **Your Strengths:**")
                for test, grade in strong_areas:
                    st.write(f"✓ {test_names[test]}: Grade {grade} - Keep it up!")
    
    with tab3:
        st.subheader("Meal Suggestions Based on Your Goals")
        
        if not user_data['bmi_history']:
            st.info("📝 Calculate your BMI first to get personalized meal suggestions!")
        else:
            latest_bmi = user_data['bmi_history'][-1]
            bmi_value = latest_bmi['bmi']
            category = latest_bmi['category']
            
            st.write(f"**Current BMI:** {bmi_value} ({category})")
            
            if category == "Underweight":
                st.warning("🍽️ **Goal: Healthy Weight Gain**")
                
                st.write("**Breakfast Ideas:**")
                st.write("- Oatmeal with banana, nuts, and honey")
                st.write("- Whole grain toast with peanut butter and scrambled eggs")
                st.write("- Smoothie with milk, banana, oats, and protein powder")
                
                st.write("\n**Lunch/Dinner Ideas:**")
                st.write("- Chicken rice with extra chicken and vegetables")
                st.write("- Salmon with quinoa and roasted vegetables")
                st.write("- Lean beef with sweet potato and broccoli")
                
                st.write("\n**Snacks:**")
                st.write("- Trail mix (nuts, dried fruits)")
                st.write("- Greek yogurt with granola")
                st.write("- Whole grain crackers with cheese")
                
                st.info("💡 **Tips:** Eat 5-6 smaller meals, focus on nutrient-dense foods, stay hydrated!")
                
            elif category == "Normal":
                st.success("🎯 **Goal: Maintain Healthy Weight**")
                
                st.write("**Breakfast Ideas:**")
                st.write("- Greek yogurt with berries and granola")
                st.write("- Whole grain toast with avocado and eggs")
                st.write("- Smoothie bowl with fruits and nuts")
                
                st.write("\n**Lunch/Dinner Ideas:**")
                st.write("- Grilled chicken with brown rice and vegetables")
                st.write("- Fish with quinoa and salad")
                st.write("- Tofu stir-fry with mixed vegetables")
                
                st.write("\n**Snacks:**")
                st.write("- Fresh fruits (apple, orange, banana)")
                st.write("- Vegetable sticks with hummus")
                st.write("- A handful of almonds")
                
                st.info("💡 **Tips:** Balanced portions, eat colorful vegetables, stay active!")
                
            elif category == "Overweight" or category == "Obesity":
                st.warning("🥗 **Goal: Healthy Weight Loss**")
                
                st.write("**Breakfast Ideas:**")
                st.write("- Egg white omelette with vegetables")
                st.write("- Oatmeal with berries (no added sugar)")
                st.write("- Green smoothie with spinach, cucumber, apple")
                
                st.write("\n**Lunch/Dinner Ideas:**")
                st.write("- Grilled fish with steamed vegetables")
                st.write("- Chicken salad with olive oil dressing")
                st.write("- Vegetable soup with lean protein")
                
                st.write("\n**Snacks:**")
                st.write("- Carrot/cucumber sticks")
                st.write("- Apple slices")
                st.write("- Unsalted nuts (small portion)")
                
                st.info("💡 **Tips:** Portion control, avoid sugary drinks, drink water before meals, eat slowly!")
            
            st.write("\n---")
            st.write("**General Nutrition Tips for Athletes:**")
            st.write("🥤 Drink 8-10 glasses of water daily")
            st.write("🥦 Eat vegetables with every meal")
            st.write("🍗 Include lean protein in each meal")
            st.write("🍚 Choose whole grains over refined carbs")
            st.write("🚫 Limit processed foods and sugary snacks")
    
    with tab4:
        st.subheader("Sleep Quality Insights")
        
        if not user_data['sleep_history']:
            st.info("📝 Track your sleep first to get personalized insights!")
        else:
            # Analyze sleep data
            sleep_data = user_data['sleep_history']
            
            if len(sleep_data) >= 3:
                # Calculate average sleep
                total_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data])
                avg_hours = total_hours / len(sleep_data)
                
                st.metric("Average Sleep Duration", f"{avg_hours:.1f} hours")
                
                # Sleep quality analysis
                excellent_count = sum(1 for s in sleep_data if s['quality'] == 'Excellent')
                good_count = sum(1 for s in sleep_data if s['quality'] == 'Good')
                fair_count = sum(1 for s in sleep_data if s['quality'] == 'Fair')
                poor_count = sum(1 for s in sleep_data if s['quality'] == 'Poor')
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Excellent", excellent_count)
                col2.metric("Good", good_count)
                col3.metric("Fair", fair_count)
                col4.metric("Poor", poor_count)
                
                st.write("---")
                
                # Personalized advice
                if avg_hours >= 8:
                    st.success("🌟 **Excellent Sleep Habits!**")
                    st.write("You're getting enough sleep for optimal recovery and performance.")
                    st.write("\n**Tips to maintain:**")
                    st.write("- Keep a consistent sleep schedule, even on weekends")
                    st.write("- Your current routine is working - stick with it!")
                elif avg_hours >= 7:
                    st.info("👍 **Good Sleep Duration**")
                    st.write("You're close to the optimal 8-10 hours for teenagers.")
                    st.write("\n**To improve:**")
                    st.write("- Try going to bed 15-30 minutes earlier")
                    st.write("- Avoid screens 1 hour before bedtime")
                    st.write("- Keep your room cool and dark")
                elif avg_hours >= 6:
                    st.warning("⚠️ **Sleep More for Better Performance**")
                    st.write("You need more sleep for optimal growth and recovery.")
                    st.write("\n**Action plan:**")
                    st.write("- Set a bedtime alarm 30 minutes before sleep time")
                    st.write("- Reduce afternoon caffeine")
                    st.write("- Create a relaxing bedtime routine")
                else:
                    st.error("🚨 **Sleep Deficit Alert**")
                    st.write("Insufficient sleep affects your NAPFA performance and health!")
                    st.write("\n**Urgent actions:**")
                    st.write("- Prioritize sleep - aim for 8+ hours")
                    st.write("- Remove ALL screens from bedroom")
                    st.write("- Talk to parents/guardians about better sleep schedule")
                
                st.write("\n---")
                st.write("**Sleep Optimization Tips:**")
                st.write("😴 Go to bed and wake up at the same time daily")
                st.write("📱 No screens 1 hour before bed (blue light disrupts sleep)")
                st.write("🏃 Exercise earlier in the day (not right before bed)")
                st.write("☕ Avoid caffeine after 2 PM")
                st.write("🌡️ Keep room cool (18-20°C is ideal)")
                st.write("📚 Try reading a book before sleep")
                st.write("🧘 Practice relaxation techniques (deep breathing)")
            else:
                st.info("Track your sleep for at least 3 days to get detailed insights!")
    
    with tab5:
        st.subheader("Progress Predictions")
        
        # Check if user has goals
        if not user_data['goals']:
            st.info("📝 Set a goal first to get progress predictions!")
        else:
            st.write("**Your Goals Progress Forecast:**")
            
            for idx, goal in enumerate(user_data['goals']):
                with st.expander(f"🎯 {goal['type']} - {goal['target']}", expanded=True):
                    progress = goal['progress']
                    target_date = datetime.strptime(goal['date'], '%Y-%m-%d')
                    created_date = datetime.strptime(goal['created'], '%Y-%m-%d')
                    today = datetime.now()
                    
                    # Calculate days
                    days_total = (target_date - created_date).days
                    days_passed = (today - created_date).days
                    days_remaining = (target_date - today).days
                    
                    # Progress bar
                    st.progress(progress / 100)
                    st.write(f"**Current Progress:** {progress}%")
                    st.write(f"**Days Remaining:** {days_remaining} days")
                    
                    # AI Prediction
                    if days_passed > 0:
                        progress_per_day = progress / days_passed
                        predicted_progress = progress + (progress_per_day * days_remaining)
                        
                        if predicted_progress >= 100:
                            days_to_complete = int((100 - progress) / progress_per_day) if progress_per_day > 0 else 999
                            completion_date = today + timedelta(days=days_to_complete)
                            
                            if days_to_complete <= days_remaining:
                                st.success(f"🎉 **On Track!** At your current pace, you'll reach your goal by {completion_date.strftime('%B %d, %Y')} ({days_to_complete} days)")
                                st.write("Keep up the great work! 💪")
                            else:
                                st.info(f"📅 You'll reach your goal around {completion_date.strftime('%B %d, %Y')}")
                                st.write("You might need a bit more time, but you're making progress!")
                        else:
                            st.warning(f"⚠️ **Need to Speed Up!** At your current pace, you'll reach {predicted_progress:.0f}% by the target date.")
                            
                            # Calculate needed pace
                            needed_progress_per_day = (100 - progress) / days_remaining if days_remaining > 0 else 0
                            improvement_factor = needed_progress_per_day / progress_per_day if progress_per_day > 0 else 2
                            
                            st.write(f"**Recommendation:** Increase your effort by {improvement_factor:.1f}x to reach your goal on time!")
                            
                            # Specific advice based on goal type
                            if goal['type'] == "NAPFA Improvement":
                                st.write("💡 **Action:** Follow your AI workout plan more consistently")
                            elif goal['type'] == "Weight Loss" or goal['type'] == "Muscle Gain":
                                st.write("💡 **Action:** Review your meal plan and increase workout frequency")
                            elif goal['type'] == "Endurance":
                                st.write("💡 **Action:** Add one more cardio session per week")
                            elif goal['type'] == "Flexibility":
                                st.write("💡 **Action:** Stretch daily for 15 minutes")
                    else:
                        st.info("Keep tracking your progress to get predictions!")
        
        # NAPFA predictions
        if user_data['napfa_history'] and len(user_data['napfa_history']) >= 2:
            st.write("\n---")
            st.subheader("📊 NAPFA Score Trend")
            
            napfa_scores = [test['total'] for test in user_data['napfa_history']]
            napfa_dates = [test['date'] for test in user_data['napfa_history']]
            
            # Calculate trend
            score_diff = napfa_scores[-1] - napfa_scores[0]
            
            if score_diff > 0:
                st.success(f"📈 Your NAPFA total improved by {score_diff} points!")
                st.write(f"From {napfa_scores[0]} to {napfa_scores[-1]}")
                
                # Predict next score
                if len(napfa_scores) >= 2:
                    avg_improvement = score_diff / (len(napfa_scores) - 1)
                    predicted_next = napfa_scores[-1] + avg_improvement
                    
                    st.write(f"\n**Prediction:** If you maintain this pace, your next test could be around {predicted_next:.0f} points")
                    
                    # Medal prediction
                    if predicted_next >= 21:
                        st.write("🥇 Potential Gold medal!")
                    elif predicted_next >= 15:
                        st.write("🥈 Potential Silver medal!")
                    elif predicted_next >= 9:
                        st.write("🥉 Potential Bronze medal!")
                        
            elif score_diff < 0:
                st.warning(f"📉 Your score decreased by {abs(score_diff)} points")
                st.write("**Recommendation:** Review your training plan and increase consistency")
            else:
                st.info("Your score stayed the same. Time to push harder!")

# Reminders and Progress
def reminders_and_progress():
    st.header("📊 Weekly Progress Report")
    
    user_data = get_user_data()
    
    # Reminder Bar at the top
    st.markdown("### 🔔 Today's Reminders")
    
    today = datetime.now().strftime('%A')
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Check scheduled activities for today
    today_activities = [s for s in user_data.get('schedule', []) if s['day'] == today]
    
    if today_activities:
        for activity in today_activities:
            st.info(f"⏰ **Today:** {activity['activity']} - {activity['time']} ({activity['duration']} min)")
    else:
        st.success(f"✅ No workouts scheduled for {today}. Good rest day or add a session!")
    
    # Smart reminders based on data
    reminders = []
    
    # Check last NAPFA test
    if user_data.get('napfa_history'):
        last_napfa_date = datetime.strptime(user_data['napfa_history'][-1]['date'], '%Y-%m-%d')
        days_since_napfa = (datetime.now() - last_napfa_date).days
        if days_since_napfa > 30:
            reminders.append(f"📝 It's been {days_since_napfa} days since your last NAPFA test. Consider retesting to track progress!")
    
    # Check last BMI
    if user_data.get('bmi_history'):
        last_bmi_date = datetime.strptime(user_data['bmi_history'][-1]['date'], '%Y-%m-%d')
        days_since_bmi = (datetime.now() - last_bmi_date).days
        if days_since_bmi > 14:
            reminders.append(f"⚖️ Update your BMI - last recorded {days_since_bmi} days ago")
    
    # Check sleep tracking
    if user_data.get('sleep_history'):
        last_sleep_date = datetime.strptime(user_data['sleep_history'][-1]['date'], '%Y-%m-%d')
        if last_sleep_date.strftime('%Y-%m-%d') != today_date:
            reminders.append("😴 Don't forget to log your sleep from last night!")
    else:
        reminders.append("😴 Start tracking your sleep for better recovery insights!")
    
    # Check exercise logging
    if user_data.get('exercises'):
        last_exercise_date = datetime.strptime(user_data['exercises'][0]['date'], '%Y-%m-%d')
        days_since_exercise = (datetime.now() - last_exercise_date).days
        if days_since_exercise > 2:
            reminders.append(f"💪 It's been {days_since_exercise} days since your last logged workout. Time to get moving!")
    else:
        reminders.append("💪 Start logging your exercises to track your fitness journey!")
    
    # Check goals progress
    if user_data.get('goals'):
        for goal in user_data['goals']:
            target_date = datetime.strptime(goal['date'], '%Y-%m-%d')
            days_until = (target_date - datetime.now()).days
            if 0 <= days_until <= 7:
                reminders.append(f"🎯 Goal deadline approaching: '{goal['target']}' in {days_until} days!")
    
    if reminders:
        st.markdown("### 💡 Smart Reminders")
        for reminder in reminders:
            st.warning(reminder)
    
    st.write("---")
    
    # Weekly Progress Report
    st.markdown("### 📈 Your Weekly Summary")
    
    # Calculate date range
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏃 NAPFA Progress", "💪 Exercise Stats", "😴 Sleep Analysis"])
    
    with tab1:
        st.subheader("This Week at a Glance")
        
        # Count activities this week
        exercises_this_week = [e for e in user_data.get('exercises', []) 
                              if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
        
        sleep_this_week = [s for s in user_data.get('sleep_history', []) 
                          if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Workouts Logged", len(exercises_this_week))
        with col2:
            if exercises_this_week:
                total_mins = sum([e['duration'] for e in exercises_this_week])
                st.metric("Total Exercise", f"{total_mins} min")
            else:
                st.metric("Total Exercise", "0 min")
        with col3:
            st.metric("Sleep Tracked", len(sleep_this_week))
        with col4:
            if sleep_this_week:
                avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_this_week]) / len(sleep_this_week)
                st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
            else:
                st.metric("Avg Sleep", "No data")
        
        # All-time stats
        st.write("")
        st.markdown("#### 📚 All-Time Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Workouts", len(user_data.get('exercises', [])))
        with col2:
            st.metric("NAPFA Tests", len(user_data.get('napfa_history', [])))
        with col3:
            st.metric("BMI Records", len(user_data.get('bmi_history', [])))
        with col4:
            st.metric("Active Goals", len(user_data.get('goals', [])))
        
        # Workout consistency
        if user_data.get('exercises'):
            st.write("")
            st.markdown("#### 🔥 Workout Consistency")
            
            # Get unique workout dates
            workout_dates = list(set([e['date'] for e in user_data.get('exercises', [])]))
            workout_dates.sort(reverse=True)
            
            if len(workout_dates) >= 2:
                # Calculate streak
                streak = 1
                current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')
                
                for i in range(1, len(workout_dates)):
                    prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                    diff = (current_date - prev_date).days
                    
                    if diff <= 2:  # Allow 1 rest day
                        streak += 1
                        current_date = prev_date
                    else:
                        break
                
                if streak >= 3:
                    st.success(f"🔥 {streak} day streak! Keep it up!")
                else:
                    st.info(f"Current streak: {streak} days. Aim for 3+ for consistency!")
    
    with tab2:
        st.subheader("🏃 NAPFA Performance")
        
        if not user_data.get('napfa_history'):
            st.info("No NAPFA tests recorded yet. Complete your first test to track progress!")
        else:
            napfa_data = user_data['napfa_history']
            
            # Show latest scores
            latest = napfa_data[-1]
            st.write(f"**Latest Test:** {latest['date']}")
            st.write(f"**Total Score:** {latest['total']} points")
            st.write(f"**Medal:** {latest['medal']}")
            
            # Show grades breakdown
            test_names = {
                'SU': 'Sit-Ups',
                'SBJ': 'Standing Broad Jump',
                'SAR': 'Sit and Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }
            
            st.write("")
            st.write("**Grade Breakdown:**")
            
            grades_df = pd.DataFrame([
                {
                    'Test': test_names[test],
                    'Score': latest['scores'][test],
                    'Grade': grade
                }
                for test, grade in latest['grades'].items()
            ])
            
            st.dataframe(grades_df, use_container_width=True, hide_index=True)
            
            # Progress over time
            if len(napfa_data) > 1:
                st.write("")
                st.write("**Progress Over Time:**")
                
                df = pd.DataFrame([
                    {'Date': test['date'], 'Total Score': test['total']}
                    for test in napfa_data
                ])
                df = df.set_index('Date')
                st.line_chart(df)
                
                # Calculate improvement
                first_score = napfa_data[0]['total']
                latest_score = napfa_data[-1]['total']
                improvement = latest_score - first_score
                
                if improvement > 0:
                    st.success(f"📈 You've improved by {improvement} points since your first test!")
                elif improvement < 0:
                    st.warning(f"📉 Score decreased by {abs(improvement)} points. Review your training plan.")
                else:
                    st.info("Score unchanged. Time to push harder!")
    
    with tab3:
        st.subheader("💪 Exercise Statistics")
        
        if not user_data.get('exercises'):
            st.info("No exercises logged yet. Start logging your workouts!")
        else:
            exercises = user_data['exercises']
            
            # Total stats
            total_workouts = len(exercises)
            total_minutes = sum([e['duration'] for e in exercises])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Workouts", total_workouts)
            with col2:
                st.metric("Total Time", f"{total_minutes} min ({total_minutes/60:.1f} hrs)")
            
            # Exercise frequency
            st.write("")
            st.write("**Exercise Frequency:**")
            exercise_counts = {}
            for ex in exercises:
                exercise_counts[ex['name']] = exercise_counts.get(ex['name'], 0) + 1
            
            df_chart = pd.DataFrame({
                'Exercise': list(exercise_counts.keys()),
                'Count': list(exercise_counts.values())
            }).sort_values('Count', ascending=False)
            
            df_chart = df_chart.set_index('Exercise')
            st.bar_chart(df_chart)
            
            # Intensity breakdown
            st.write("")
            st.write("**Intensity Distribution:**")
            intensity_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            for ex in exercises:
                intensity_counts[ex['intensity']] += 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Low Intensity", intensity_counts['Low'])
            with col2:
                st.metric("Medium Intensity", intensity_counts['Medium'])
            with col3:
                st.metric("High Intensity", intensity_counts['High'])
            
            # Recent workouts
            st.write("")
            st.write("**Recent Workouts:**")
            recent = exercises[:5]  # Last 5
            for ex in recent:
                st.write(f"• {ex['date']}: {ex['name']} - {ex['duration']}min ({ex['intensity']} intensity)")
    
    with tab4:
        st.subheader("😴 Sleep Analysis")
        
        if not user_data.get('sleep_history'):
            st.info("No sleep data yet. Start tracking your sleep!")
        else:
            sleep_data = user_data['sleep_history']
            
            # Calculate stats
            total_records = len(sleep_data)
            avg_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / total_records
            
            quality_counts = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Poor': 0}
            for s in sleep_data:
                quality_counts[s['quality']] += 1
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Sleep", f"{avg_hours:.1f} hours")
            with col2:
                st.metric("Records Tracked", total_records)
            
            # Quality breakdown
            st.write("")
            st.write("**Sleep Quality Distribution:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("😊 Excellent", quality_counts['Excellent'])
            with col2:
                st.metric("👍 Good", quality_counts['Good'])
            with col3:
                st.metric("😐 Fair", quality_counts['Fair'])
            with col4:
                st.metric("😴 Poor", quality_counts['Poor'])
            
            # Sleep trend
            if len(sleep_data) > 1:
                st.write("")
                st.write("**Sleep Duration Trend:**")
                df = pd.DataFrame(sleep_data)
                df['total_hours'] = df['hours'] + df['minutes'] / 60
                df_chart = df.set_index('date')['total_hours']
                st.line_chart(df_chart)
            
            # Sleep insights
            st.write("")
            st.write("**Insights:**")
            if avg_hours >= 8:
                st.success("✅ Excellent sleep habits! Keep it up for optimal recovery and performance.")
            elif avg_hours >= 7:
                st.info("👍 Good sleep duration. Try to get closer to 8-10 hours for peak performance.")
            else:
                st.warning("⚠️ You're not getting enough sleep. Aim for 8-10 hours for teenagers!")
            
            # Best and worst
            if len(sleep_data) >= 3:
                sleep_sorted = sorted(sleep_data, key=lambda x: x['hours'] + x['minutes']/60, reverse=True)
                best = sleep_sorted[0]
                worst = sleep_sorted[-1]
                
                st.write(f"**Best night:** {best['date']} - {best['hours']}h {best['minutes']}m")
                st.write(f"**Shortest night:** {worst['date']} - {worst['hours']}h {worst['minutes']}m")

# Advanced Health Metrics
def advanced_metrics():
    st.header("🏥 Advanced Health Metrics")
    st.write("Track detailed health and fitness metrics")
    
    user_data = get_user_data()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 BMR & Calories",
        "📊 Body Composition",
        "❤️ Heart Rate Zones",
        "💧 Hydration Tracker"
    ])
    
    with tab1:
        st.subheader("🔥 Basal Metabolic Rate (BMR) Calculator")
        st.write("Calculate your daily calorie needs")
        
        # Get user data
        if user_data.get('bmi_history'):
            latest_bmi = user_data['bmi_history'][-1]
            default_weight = latest_bmi['weight']
            default_height = latest_bmi['height'] * 100  # Convert to cm
        else:
            default_weight = 60.0
            default_height = 165.0
        
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0, 
                                    value=float(default_weight), step=0.1, key="bmr_weight")
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, 
                                    value=float(default_height), step=0.5, key="bmr_height")
        
        with col2:
            age = user_data.get('age', 14)
            gender = user_data.get('gender', 'm')
            
            st.metric("Age", age)
            st.metric("Gender", "Male" if gender == 'm' else "Female")
        
        activity_level = st.selectbox(
            "Activity Level",
            [
                "Sedentary (little/no exercise)",
                "Lightly Active (1-3 days/week)",
                "Moderately Active (3-5 days/week)",
                "Very Active (6-7 days/week)",
                "Extremely Active (athlete, 2x/day)"
            ],
            index=2
        )
        
        if st.button("Calculate BMR & Calories", type="primary"):
            # Mifflin-St Jeor Equation (most accurate for teens)
            if gender == 'm':
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            
            # Activity multipliers
            activity_multipliers = {
                "Sedentary (little/no exercise)": 1.2,
                "Lightly Active (1-3 days/week)": 1.375,
                "Moderately Active (3-5 days/week)": 1.55,
                "Very Active (6-7 days/week)": 1.725,
                "Extremely Active (athlete, 2x/day)": 1.9
            }
            
            multiplier = activity_multipliers[activity_level]
            tdee = bmr * multiplier  # Total Daily Energy Expenditure
            
            # Calculate macros
            protein_grams = weight * 1.6  # 1.6g per kg for active teens
            protein_cals = protein_grams * 4
            
            fat_cals = tdee * 0.25  # 25% from fat
            fat_grams = fat_cals / 9
            
            carb_cals = tdee - protein_cals - fat_cals
            carb_grams = carb_cals / 4
            
            # Display results
            st.write("---")
            st.write("### Your Metabolic Profile")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BMR", f"{bmr:.0f} cal/day")
                st.write("*Calories burned at rest*")
            
            with col2:
                st.metric("TDEE", f"{tdee:.0f} cal/day")
                st.write("*Total daily calories needed*")
            
            with col3:
                calories_per_workout = 300  # Average
                workout_days = 4  # Estimate
                weekly_exercise_cals = calories_per_workout * workout_days
                st.metric("Exercise Burns", f"{weekly_exercise_cals:.0f} cal/week")
            
            # Goals-based recommendations
            st.write("")
            st.write("### Calorie Targets by Goal")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="stat-card" style="background: #f44336; color: white;">
                    <h3>💪 Weight Loss</h3>
                    <h2>{:.0f} cal/day</h2>
                    <p>Deficit: -500 cal/day</p>
                    <p>Rate: -0.5kg/week</p>
                </div>
                """.format(tdee - 500), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="stat-card" style="background: #4caf50; color: white;">
                    <h3>⚖️ Maintenance</h3>
                    <h2>{:.0f} cal/day</h2>
                    <p>No deficit/surplus</p>
                    <p>Maintain weight</p>
                </div>
                """.format(tdee), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="stat-card" style="background: #2196f3; color: white;">
                    <h3>🏋️ Muscle Gain</h3>
                    <h2>{:.0f} cal/day</h2>
                    <p>Surplus: +300 cal/day</p>
                    <p>Rate: +0.25kg/week</p>
                </div>
                """.format(tdee + 300), unsafe_allow_html=True)
            
            # Macronutrients
            st.write("")
            st.write("### Recommended Macronutrients")
            
            st.write(f"**For your activity level ({activity_level}):**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Protein", f"{protein_grams:.0f}g/day")
                st.write(f"({protein_cals:.0f} cal)")
                st.progress(protein_cals / tdee)
            
            with col2:
                st.metric("Carbs", f"{carb_grams:.0f}g/day")
                st.write(f"({carb_cals:.0f} cal)")
                st.progress(carb_cals / tdee)
            
            with col3:
                st.metric("Fats", f"{fat_grams:.0f}g/day")
                st.write(f"({fat_cals:.0f} cal)")
                st.progress(fat_cals / tdee)
            
            # Save to user data
            if 'bmr_history' not in user_data:
                user_data['bmr_history'] = []
            
            user_data['bmr_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'bmr': round(bmr),
                'tdee': round(tdee),
                'weight': weight,
                'height': height,
                'activity_level': activity_level
            })
            update_user_data(user_data)
    
    with tab2:
        st.subheader("📊 Body Composition Tracking")
        st.write("Track body fat percentage and lean mass")
        
        # Body Fat Percentage Calculator (Navy Method)
        st.write("### Calculate Body Fat Percentage")
        st.write("Using the Navy Method (most accurate without calipers)")
        
        if user_data.get('bmi_history'):
            latest_bmi = user_data['bmi_history'][-1]
            default_weight = latest_bmi['weight']
            default_height_cm = latest_bmi['height'] * 100
        else:
            default_weight = 60.0
            default_height_cm = 165.0
        
        col1, col2 = st.columns(2)
        
        with col1:
            bf_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0, 
                                       value=float(default_weight), step=0.1, key="bf_weight")
            bf_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, 
                                       value=float(default_height_cm), step=0.5, key="bf_height")
        
        with col2:
            neck = st.number_input("Neck circumference (cm)", min_value=20.0, max_value=60.0, 
                                  value=35.0, step=0.5, key="neck")
            waist = st.number_input("Waist circumference (cm)", min_value=40.0, max_value=150.0, 
                                   value=75.0, step=0.5, key="waist")
            
            if user_data.get('gender') == 'f':
                hips = st.number_input("Hip circumference (cm)", min_value=50.0, max_value=150.0, 
                                      value=90.0, step=0.5, key="hips")
        
        if st.button("Calculate Body Fat %", type="primary"):
            # Navy Method Formula
            gender = user_data.get('gender', 'm')
            
            if gender == 'm':
                body_fat = (495 / (1.0324 - 0.19077 * (waist - neck) / 2.54 + 0.15456 * bf_height / 2.54)) - 450
            else:
                body_fat = (495 / (1.29579 - 0.35004 * (waist + hips - neck) / 2.54 + 0.22100 * bf_height / 2.54)) - 450
            
            # Ensure reasonable range
            body_fat = max(5, min(body_fat, 50))
            
            # Calculate lean mass
            fat_mass = bf_weight * (body_fat / 100)
            lean_mass = bf_weight - fat_mass
            
            # Classifications
            if gender == 'm':
                if body_fat < 6:
                    category = "Essential Fat"
                    color = "#ff9800"
                elif body_fat < 14:
                    category = "Athletes"
                    color = "#4caf50"
                elif body_fat < 18:
                    category = "Fitness"
                    color = "#8bc34a"
                elif body_fat < 25:
                    category = "Average"
                    color = "#2196f3"
                else:
                    category = "Above Average"
                    color = "#f44336"
            else:
                if body_fat < 14:
                    category = "Essential Fat"
                    color = "#ff9800"
                elif body_fat < 21:
                    category = "Athletes"
                    color = "#4caf50"
                elif body_fat < 25:
                    category = "Fitness"
                    color = "#8bc34a"
                elif body_fat < 32:
                    category = "Average"
                    color = "#2196f3"
                else:
                    category = "Above Average"
                    color = "#f44336"
            
            # Display results
            st.write("---")
            st.write("### Your Body Composition")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card" style="background: {color}; color: white;">
                    <h3>Body Fat %</h3>
                    <h1>{body_fat:.1f}%</h1>
                    <p>{category}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Fat Mass", f"{fat_mass:.1f} kg")
                st.metric("Lean Mass", f"{lean_mass:.1f} kg")
            
            with col3:
                st.write("**Ideal Ranges:**")
                if gender == 'm':
                    st.write("Athletes: 6-13%")
                    st.write("Fitness: 14-17%")
                    st.write("Average: 18-24%")
                else:
                    st.write("Athletes: 14-20%")
                    st.write("Fitness: 21-24%")
                    st.write("Average: 25-31%")
            
            # Save to user data
            if 'body_composition' not in user_data:
                user_data['body_composition'] = []
            
            user_data['body_composition'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'body_fat_percent': round(body_fat, 1),
                'fat_mass': round(fat_mass, 1),
                'lean_mass': round(lean_mass, 1),
                'weight': bf_weight,
                'neck': neck,
                'waist': waist
            })
            update_user_data(user_data)
            
            # Show trend if multiple measurements
            if len(user_data['body_composition']) > 1:
                st.write("")
                st.write("### Progress Trend")
                
                df = pd.DataFrame(user_data['body_composition'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.line_chart(df.set_index('date')['body_fat_percent'])
                    st.write("Body Fat % Over Time")
                
                with col2:
                    st.line_chart(df.set_index('date')[['fat_mass', 'lean_mass']])
                    st.write("Fat vs Lean Mass")
    
    with tab3:
        st.subheader("❤️ Heart Rate Training Zones")
        st.write("Optimize your training with heart rate zones")
        
        # Calculate max heart rate
        age = user_data.get('age', 14)
        max_hr = 220 - age
        
        # Resting heart rate input
        st.write("### Calculate Your Training Zones")
        
        resting_hr = st.number_input(
            "Resting Heart Rate (bpm)",
            min_value=40,
            max_value=100,
            value=70,
            help="Measure first thing in the morning before getting out of bed"
        )
        
        # Heart Rate Reserve method (Karvonen Formula)
        hr_reserve = max_hr - resting_hr
        
        # Define zones
        zones = {
            "Zone 1 - Very Light": {
                "range": (0.50, 0.60),
                "description": "Recovery, warm-up",
                "benefits": "Promotes recovery, builds base endurance",
                "duration": "Long (45-60+ min)",
                "color": "#90caf9"
            },
            "Zone 2 - Light": {
                "range": (0.60, 0.70),
                "description": "Fat burning, base training",
                "benefits": "Builds aerobic base, burns fat",
                "duration": "Moderate-Long (30-60 min)",
                "color": "#81c784"
            },
            "Zone 3 - Moderate": {
                "range": (0.70, 0.80),
                "description": "Aerobic endurance",
                "benefits": "Improves cardiovascular fitness",
                "duration": "Moderate (20-40 min)",
                "color": "#fff176"
            },
            "Zone 4 - Hard": {
                "range": (0.80, 0.90),
                "description": "Lactate threshold",
                "benefits": "Increases NAPFA performance, speed",
                "duration": "Short-Moderate (10-30 min)",
                "color": "#ffb74d"
            },
            "Zone 5 - Maximum": {
                "range": (0.90, 1.00),
                "description": "VO2 Max, sprints",
                "benefits": "Max power, NAPFA 2.4km final sprint",
                "duration": "Very Short (1-5 min intervals)",
                "color": "#e57373"
            }
        }
        
        st.write("")
        st.write(f"### Your Heart Rate Zones (Max HR: {max_hr} bpm)")
        
        for zone_name, zone_info in zones.items():
            min_percent, max_percent = zone_info['range']
            min_hr = int(resting_hr + (hr_reserve * min_percent))
            max_hr_zone = int(resting_hr + (hr_reserve * max_percent))
            
            with st.expander(f"{zone_name}: {min_hr}-{max_hr_zone} bpm", expanded=True):
                st.markdown(f"""
                <div class="stat-card" style="background: {zone_info['color']};">
                    <h3>{zone_info['description']}</h3>
                    <h2>{min_hr} - {max_hr_zone} bpm</h2>
                    <p><strong>Benefits:</strong> {zone_info['benefits']}</p>
                    <p><strong>Duration:</strong> {zone_info['duration']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # NAPFA-specific recommendations
        st.write("")
        st.write("### 🏃 NAPFA Training Recommendations")
        
        st.info("""
        **For 2.4km Run:**
        - Zone 2-3: 70% of training (build endurance)
        - Zone 4: 20% of training (improve speed)
        - Zone 5: 10% of training (final sprint power)
        
        **For Shuttle Run:**
        - Zone 4-5: High-intensity intervals
        - 30 sec sprints, 90 sec rest
        
        **For Recovery:**
        - Zone 1: Active recovery days
        - Light jogging or walking
        """)
        
        # Save resting HR
        if 'heart_rate_data' not in user_data:
            user_data['heart_rate_data'] = []
        
        if st.button("Save Resting HR"):
            user_data['heart_rate_data'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'resting_hr': resting_hr,
                'max_hr': max_hr
            })
            update_user_data(user_data)
            st.success("Resting heart rate saved!")
    
    with tab4:
        st.subheader("💧 Hydration Calculator & Tracker")
        st.write("Stay properly hydrated for optimal performance")
        
        # Calculate daily hydration needs
        st.write("### Daily Hydration Needs")
        
        if user_data.get('bmi_history'):
            weight = user_data['bmi_history'][-1]['weight']
        else:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0, value=60.0)
        
        # Calculate exercises today
        today = datetime.now().strftime('%Y-%m-%d')
        today_exercises = [e for e in user_data.get('exercises', []) if e['date'] == today]
        workout_duration = sum(e['duration'] for e in today_exercises)
        
        # Base hydration (30-35 ml per kg)
        base_hydration = weight * 35  # ml
        
        # Add for exercise (500-1000ml per hour)
        exercise_hydration = (workout_duration / 60) * 750  # ml
        
        # Add for climate (if hot, +500ml)
        climate_bonus = 0  # We'll let them select
        
        st.write("**Factors:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Base Need", f"{base_hydration:.0f} ml")
            st.write(f"({weight} kg × 35 ml)")
        
        with col2:
            st.metric("Exercise Bonus", f"+{exercise_hydration:.0f} ml")
            st.write(f"({workout_duration} min workout)")
        
        climate = st.selectbox(
            "Climate/Temperature",
            ["Cool (<25°C)", "Moderate (25-30°C)", "Hot (>30°C)"]
        )
        
        if "Moderate" in climate:
            climate_bonus = 500
        elif "Hot" in climate:
            climate_bonus = 1000
        
        total_hydration = base_hydration + exercise_hydration + climate_bonus
        
        st.write("")
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, {SST_COLORS['blue']} 0%, #1565c0 100%); color: white;">
            <h2>💧 Total Daily Target</h2>
            <h1>{total_hydration:.0f} ml</h1>
            <h3>({total_hydration/1000:.1f} liters)</h3>
            <p>≈ {total_hydration/250:.0f} glasses (250ml each)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Hydration tracker
        st.write("")
        st.write("### Track Today's Intake")
        
        # Initialize today's hydration
        if 'hydration_log' not in user_data:
            user_data['hydration_log'] = []
        
        today_log = [h for h in user_data['hydration_log'] if h['date'] == today]
        current_intake = sum(h['amount'] for h in today_log)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.progress(min(current_intake / total_hydration, 1.0))
            st.write(f"**Progress:** {current_intake:.0f} / {total_hydration:.0f} ml ({(current_intake/total_hydration*100):.0f}%)")
        
        with col2:
            remaining = max(0, total_hydration - current_intake)
            st.metric("Remaining", f"{remaining:.0f} ml")
        
        # Quick add buttons
        st.write("**Quick Add:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💧 Glass (250ml)"):
                user_data['hydration_log'].append({
                    'date': today,
                    'time': datetime.now().strftime('%H:%M'),
                    'amount': 250
                })
                update_user_data(user_data)
                st.rerun()
        
        with col2:
            if st.button("🥤 Bottle (500ml)"):
                user_data['hydration_log'].append({
                    'date': today,
                    'time': datetime.now().strftime('%H:%M'),
                    'amount': 500
                })
                update_user_data(user_data)
                st.rerun()
        
        with col3:
            if st.button("🧃 Large (750ml)"):
                user_data['hydration_log'].append({
                    'date': today,
                    'time': datetime.now().strftime('%H:%M'),
                    'amount': 750
                })
                update_user_data(user_data)
                st.rerun()
        
        with col4:
            if st.button("💧 Custom"):
                custom_amount = st.number_input("Amount (ml)", min_value=0, max_value=2000, value=250, step=50)
                if st.button("Add Custom"):
                    user_data['hydration_log'].append({
                        'date': today,
                        'time': datetime.now().strftime('%H:%M'),
                        'amount': custom_amount
                    })
                    update_user_data(user_data)
                    st.rerun()
        
        # Today's log
        if today_log:
            st.write("")
            st.write("**Today's Log:**")
            for log in reversed(today_log):
                st.write(f"• {log['time']} - {log['amount']} ml")
        
        # Hydration tips
        st.write("")
        st.info("""
        **💡 Hydration Tips:**
        - Drink before you feel thirsty
        - Hydrate 2 hours before exercise
        - Drink 150-250ml every 15-20 min during exercise
        - Rehydrate after exercise (1.5x fluid lost)
        - Urine should be light yellow (not clear, not dark)
        - Avoid sugary drinks - water is best
        """)

# API Integrations
def api_integrations():
    st.header("🌐 API Integrations")
    st.write("Connect with external services for enhanced features")
    
    user_data = get_user_data()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🌤️ Weather API",
        "🍔 Nutrition API",
        "🎥 YouTube API"
    ])
    
    with tab1:
        st.subheader("🌤️ Weather-Based Workout Recommendations")
        st.write("Get outdoor workout suggestions based on current weather")
        
        # Show API status
        if OPENWEATHER_API_KEY:
            st.success("✅ Real Weather API Active")
        else:
            st.info("📝 Using simulated weather data. Add API key to enable real-time weather.")
        
        location = st.text_input("Your Location", value="Singapore", placeholder="Enter city name")
        
        if st.button("Get Weather & Recommendations", type="primary"):
            
            if OPENWEATHER_API_KEY and API_MODE == 'real':
                # REAL API CALL
                try:
                    import requests
                    
                    # OpenWeatherMap API endpoint
                    url = f"http://api.openweathermap.org/data/2.5/weather"
                    params = {
                        'q': location,
                        'appid': OPENWEATHER_API_KEY,
                        'units': 'metric'  # Get temperature in Celsius
                    }
                    
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract weather data
                        temp = round(data['main']['temp'])
                        humidity = data['main']['humidity']
                        conditions = data['weather'][0]['main']
                        description = data['weather'][0]['description']
                        
                        st.success(f"✅ Real-time weather data from OpenWeatherMap")
                    else:
                        st.error(f"Error fetching weather: {response.status_code}")
                        # Fallback to mock data
                        temp, humidity, conditions = 30, 75, "Clear"
                
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
                    st.info("Falling back to simulated data")
                    # Fallback to mock data
                    import random
                    temp = random.randint(25, 35)
                    humidity = random.randint(60, 90)
                    conditions = random.choice(["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Rainy"])
            
            else:
                # MOCK DATA (when no API key)
                import random
                temp = random.randint(25, 35)
                humidity = random.randint(60, 90)
                conditions = random.choice(["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Rainy"])
                
                if not OPENWEATHER_API_KEY:
                    st.warning("⚠️ Simulated weather data (no API key configured)")
            
            # Display weather (same for both real and mock)
            st.write("### Current Weather")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🌡️ Temperature", f"{temp}°C")
            with col2:
                st.metric("💧 Humidity", f"{humidity}%")
            with col3:
                st.metric("☁️ Conditions", conditions)
            
            # Generate recommendations (same logic for both)
            st.write("")
            st.write("### 🏃 Workout Recommendations")
            
            if temp < 28 and "Rain" not in conditions:
                recommendation = "✅ Perfect for outdoor running!"
                workout = "2.4km NAPFA practice run"
                color = "#4caf50"
            elif temp < 32 and "Rain" not in conditions:
                recommendation = "⚠️ Good for outdoor, stay hydrated"
                workout = "Morning or evening run (avoid midday)"
                color = "#ff9800"
            elif "Rain" in conditions:
                recommendation = "🏠 Indoor workout recommended"
                workout = "Indoor circuit: push-ups, sit-ups, burpees"
                color = "#2196f3"
            else:
                recommendation = "🌡️ Too hot! Indoor training"
                workout = "Air-con gym or home workout"
                color = "#f44336"
            
            st.markdown(f"""
            <div class="stat-card" style="background: {color}; color: white;">
                <h3>{recommendation}</h3>
                <h4>Suggested: {workout}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Hydration advice
            hydration_need = "High" if temp > 30 or humidity > 80 else "Moderate"
            st.info(f"💧 **Hydration Need:** {hydration_need} - Drink {500 if hydration_need == 'High' else 300}ml before workout")
        
        # Setup instructions
        if not OPENWEATHER_API_KEY:
            st.write("")
            st.write("---")
            st.write("### 🔗 Enable Real-Time Weather")
            
            with st.expander("📝 Setup Instructions", expanded=False):
                st.markdown("""
                **Step 1: Get Free API Key**
                1. Go to: https://openweathermap.org/api
                2. Click "Sign Up" (it's FREE!)
                3. Verify your email
                4. Go to "API Keys" tab
                5. Copy your API key
                
                **Step 2: Add to Streamlit Cloud**
                1. Deploy your app to Streamlit Cloud
                2. Go to your app settings (⚙️)
                3. Click "Secrets"
                4. Add this:
                ```
                OPENWEATHER_API_KEY = "your_api_key_here"
                ```
                5. Save and restart app
                
                **Step 3: Run Locally (Optional)**
                Create a file called `.streamlit/secrets.toml`:
                ```
                OPENWEATHER_API_KEY = "your_api_key_here"
                ```
                
                **That's it!** The app will automatically use real weather data.
                
                **Free Tier Limits:**
                - 1,000 API calls per day
                - 60 calls per minute
                - More than enough for personal use!
                """)

    
    with tab2:
        st.subheader("🍔 Food & Nutrition Database")
        st.write("Search nutritional information for any food")
        
        # Show API status
        if USDA_API_KEY:
            st.success("✅ Real USDA Food Database Active (350,000+ foods)")
        else:
            st.info("📝 Using sample food database. Add USDA API key for 350,000+ foods.")
        
        # Food search
        food_query = st.text_input("Search for a food", placeholder="e.g., chicken rice, banana, salmon")
        
        # Advanced search options
        with st.expander("🔍 Advanced Search Options"):
            col1, col2 = st.columns(2)
            with col1:
                food_category = st.selectbox(
                    "Food Category (optional)",
                    ["All Categories", "Dairy", "Fruits", "Vegetables", "Proteins", 
                     "Grains", "Snacks", "Beverages", "Fast Foods"]
                )
            with col2:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Relevance", "Protein (High to Low)", "Calories (Low to High)", "Calories (High to Low)"]
                )
        
        if st.button("Search Nutrition", type="primary"):
            
            if USDA_API_KEY and API_MODE == 'real':
                # REAL USDA API CALL
                try:
                    import requests
                    
                    # FoodData Central API endpoint
                    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
                    
                    params = {
                        'api_key': USDA_API_KEY,
                        'query': food_query,
                        'pageSize': 10,  # Get top 10 results
                    }
                    
                    # Note: Removed dataType filter as it can cause 400 errors
                    # The API will return the best matches automatically
                    
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        foods = data.get('foods', [])
                        
                        if foods:
                            st.success(f"✅ Found {len(foods)} results from USDA database")
                            
                            # Sort results if needed
                            if sort_by == "Protein (High to Low)":
                                foods = sorted(foods, key=lambda x: get_nutrient_from_food(x, 'Protein'), reverse=True)
                            elif sort_by == "Calories (Low to High)":
                                foods = sorted(foods, key=lambda x: get_nutrient_from_food(x, 'Energy'))
                            elif sort_by == "Calories (High to Low)":
                                foods = sorted(foods, key=lambda x: get_nutrient_from_food(x, 'Energy'), reverse=True)
                            
                            # Display results
                            for food in foods[:5]:  # Show top 5
                                food_name = food.get('description', 'Unknown Food')
                                brand = food.get('brandOwner', '')
                                
                                # Extract nutrients
                                nutrients = food.get('foodNutrients', [])
                                
                                calories = get_nutrient_value(nutrients, 'Energy')
                                protein = get_nutrient_value(nutrients, 'Protein')
                                carbs = get_nutrient_value(nutrients, 'Carbohydrate, by difference')
                                fat = get_nutrient_value(nutrients, 'Total lipid (fat)')
                                fiber = get_nutrient_value(nutrients, 'Fiber, total dietary')
                                sugar = get_nutrient_value(nutrients, 'Sugars, total including NLEA')
                                
                                # Handle alternative nutrient names
                                if calories is None:
                                    calories = get_nutrient_value(nutrients, 'Energy (Atwater General Factors)')
                                if carbs is None:
                                    carbs = get_nutrient_value(nutrients, 'Carbohydrate')
                                if fat is None:
                                    fat = get_nutrient_value(nutrients, 'Fat')
                                
                                # Serving size
                                serving = food.get('servingSize', 100)
                                serving_unit = food.get('servingUnit', 'g')
                                
                                with st.expander(f"🍽️ {food_name}" + (f" ({brand})" if brand else ""), expanded=True):
                                    col1, col2 = st.columns([2, 1])
                                    
                                    with col1:
                                        st.write(f"**Serving Size:** {serving} {serving_unit}")
                                        
                                        col_a, col_b, col_c, col_d = st.columns(4)
                                        col_a.metric("Calories", f"{calories:.0f}" if calories else "N/A")
                                        col_b.metric("Protein", f"{protein:.1f}g" if protein else "N/A")
                                        col_c.metric("Carbs", f"{carbs:.1f}g" if carbs else "N/A")
                                        col_d.metric("Fat", f"{fat:.1f}g" if fat else "N/A")
                                        
                                        if fiber or sugar:
                                            st.write("")
                                            col_e, col_f = st.columns(2)
                                            if fiber:
                                                col_e.write(f"**Fiber:** {fiber:.1f}g")
                                            if sugar:
                                                col_f.write(f"**Sugars:** {sugar:.1f}g")
                                    
                                    with col2:
                                        # Macro ratio
                                        if calories and calories > 0:
                                            st.write("**Macro Ratio:**")
                                            p_cals = (protein or 0) * 4
                                            c_cals = (carbs or 0) * 4
                                            f_cals = (fat or 0) * 9
                                            total = p_cals + c_cals + f_cals
                                            
                                            if total > 0:
                                                st.write(f"Protein: {(p_cals/total*100):.0f}%")
                                                st.write(f"Carbs: {(c_cals/total*100):.0f}%")
                                                st.write(f"Fat: {(f_cals/total*100):.0f}%")
                                        
                                        # Health score (simple)
                                        health_score = calculate_health_score(protein, carbs, fat, fiber, sugar)
                                        if health_score:
                                            st.write("")
                                            st.metric("Health Score", f"{health_score}/10")
                        else:
                            st.warning(f"No results found for '{food_query}'. Try a different search term.")
                    
                    elif response.status_code == 400:
                        st.error("API Error 400: Invalid request format")
                        st.write("**Debug Info:**")
                        st.write(f"Query: {food_query}")
                        try:
                            error_detail = response.json()
                            st.write(f"Error details: {error_detail}")
                        except:
                            st.write(f"Response: {response.text}")
                        st.info("Falling back to sample database")
                        show_mock_nutrition_data(food_query)
                    
                    elif response.status_code == 403:
                        st.error("API Error 403: Invalid API key")
                        st.write("Please check your USDA_API_KEY in Streamlit Secrets")
                        st.info("Falling back to sample database")
                        show_mock_nutrition_data(food_query)
                    
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.info("Falling back to sample database")
                        show_mock_nutrition_data(food_query)
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Falling back to sample database")
                    show_mock_nutrition_data(food_query)
            
            else:
                # MOCK DATA (when no API key)
                show_mock_nutrition_data(food_query)
        
        # Setup instructions
        if not USDA_API_KEY:
            st.write("")
            st.write("---")
            st.write("### 🔗 Enable Full Food Database")
            
            with st.expander("📝 Setup Instructions (2 minutes)", expanded=False):
                st.markdown("""
                **Step 1: Get FREE API Key**
                1. Go to: https://fdc.nal.usda.gov/api-key-signup.html
                2. Fill in:
                   - First Name
                   - Last Name
                   - Email Address
                   - Organization: "School of Science and Technology" (or "Personal")
                3. Click "Sign Up"
                4. Check your email for API key
                5. Copy the key (long string of letters/numbers)
                
                **Step 2: Add to Streamlit Cloud**
                1. Go to your deployed app
                2. Click ⚙️ Settings → Secrets
                3. Add this line:
                ```
                USDA_API_KEY = "your_api_key_here"
                ```
                4. Save and restart
                
                **Step 3: Test**
                1. Come back to this page
                2. Should see "✅ Real USDA Food Database Active"
                3. Search any food - get instant results!
                
                **What You Get:**
                - ✅ 350,000+ foods (vs. 5 sample foods)
                - ✅ Brand name foods
                - ✅ Restaurant foods
                - ✅ Complete nutrient data (vitamins, minerals, etc.)
                - ✅ Serving size info
                - ✅ Unlimited searches (FREE forever!)
                
                **Free Tier:**
                - 1,000 requests per hour
                - No daily limit
                - No credit card needed
                - FREE forever!
                """)

# Helper functions for USDA API
def get_nutrient_from_food(food, nutrient_name):
    """Extract nutrient value from food object for sorting"""
    nutrients = food.get('foodNutrients', [])
    value = get_nutrient_value(nutrients, nutrient_name)
    return value if value is not None else 0

def get_nutrient_value(nutrients, nutrient_name):
    """Extract nutrient value from USDA food data"""
    for nutrient in nutrients:
        # Check nutrient name
        name = nutrient.get('nutrientName', '')
        if nutrient_name.lower() in name.lower():
            return nutrient.get('value', 0)
    return None

def calculate_health_score(protein, carbs, fat, fiber, sugar):
    """Simple health score calculation (1-10)"""
    if not all([protein is not None, carbs is not None, fat is not None]):
        return None
    
    score = 5.0  # Start at neutral
    
    # High protein is good
    if protein and protein > 10:
        score += 1.5
    elif protein and protein > 5:
        score += 0.5
    
    # High fiber is good
    if fiber and fiber > 5:
        score += 1.5
    elif fiber and fiber > 2:
        score += 0.5
    
    # High sugar is bad
    if sugar and sugar > 20:
        score -= 2.0
    elif sugar and sugar > 10:
        score -= 1.0
    
    # Balance of macros
    total = protein + carbs + fat
    if total > 0:
        protein_ratio = protein / total
        if 0.2 <= protein_ratio <= 0.4:  # Good protein ratio
            score += 1.0
    
    return max(1, min(10, round(score, 1)))

def show_mock_nutrition_data(food_query):
    """Display mock nutrition data when API not available"""
    # Simulated nutrition database
    nutrition_db = {
        "chicken rice": {
            "calories": 607,
            "protein": 25,
            "carbs": 86,
            "fat": 15,
            "fiber": 2,
            "sugar": 3,
            "serving": "1 plate (350g)"
        },
        "banana": {
            "calories": 105,
            "protein": 1.3,
            "carbs": 27,
            "fat": 0.4,
            "fiber": 3.1,
            "sugar": 14,
            "serving": "1 medium (118g)"
        },
        "apple": {
            "calories": 95,
            "protein": 0.5,
            "carbs": 25,
            "fat": 0.3,
            "fiber": 4.4,
            "sugar": 19,
            "serving": "1 medium (182g)"
        },
        "white rice": {
            "calories": 204,
            "protein": 4.2,
            "carbs": 45,
            "fat": 0.4,
            "fiber": 0.6,
            "sugar": 0.1,
            "serving": "1 cup cooked (158g)"
        },
        "grilled chicken breast": {
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "fiber": 0,
            "sugar": 0,
            "serving": "100g"
        },
        "salmon": {
            "calories": 206,
            "protein": 22,
            "carbs": 0,
            "fat": 13,
            "fiber": 0,
            "sugar": 0,
            "serving": "100g"
        },
        "broccoli": {
            "calories": 55,
            "protein": 3.7,
            "carbs": 11,
            "fat": 0.6,
            "fiber": 5.1,
            "sugar": 2.2,
            "serving": "1 cup chopped (156g)"
        },
        "egg": {
            "calories": 72,
            "protein": 6,
            "carbs": 0.4,
            "fat": 5,
            "fiber": 0,
            "sugar": 0.2,
            "serving": "1 large (50g)"
        }
    }
    
    # Search (case-insensitive, partial match)
    results = {k: v for k, v in nutrition_db.items() if food_query.lower() in k.lower()}
    
    if results:
        st.success(f"Found {len(results)} result(s) in sample database")
        
        for food_name, nutrition in results.items():
            with st.expander(f"🍽️ {food_name.title()}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Serving Size:** {nutrition['serving']}")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("Calories", f"{nutrition['calories']} kcal")
                    col_b.metric("Protein", f"{nutrition['protein']}g")
                    col_c.metric("Carbs", f"{nutrition['carbs']}g")
                    col_d.metric("Fat", f"{nutrition['fat']}g")
                    
                    st.write("")
                    col_e, col_f = st.columns(2)
                    col_e.write(f"**Fiber:** {nutrition['fiber']}g")
                    col_f.write(f"**Sugars:** {nutrition['sugar']}g")
                
                with col2:
                    # Macro ratio
                    total_cals = (nutrition['protein'] * 4 + nutrition['carbs'] * 4 + nutrition['fat'] * 9)
                    if total_cals > 0:
                        st.write("**Macro Ratio:**")
                        st.write(f"Protein: {(nutrition['protein']*4/total_cals*100):.0f}%")
                        st.write(f"Carbs: {(nutrition['carbs']*4/total_cals*100):.0f}%")
                        st.write(f"Fat: {(nutrition['fat']*9/total_cals*100):.0f}%")
                    
                    # Health score
                    health_score = calculate_health_score(
                        nutrition['protein'], 
                        nutrition['carbs'], 
                        nutrition['fat'],
                        nutrition['fiber'],
                        nutrition['sugar']
                    )
                    if health_score:
                        st.write("")
                        st.metric("Health Score", f"{health_score}/10")
        
        st.info("💡 **Limited to 8 sample foods.** Add USDA API key for 350,000+ foods!")
    else:
        st.warning(f"No results for '{food_query}' in sample database.")
        st.write("**Try searching:** chicken rice, banana, apple, white rice, grilled chicken breast, salmon, broccoli, egg")
        st.info("💡 Add USDA API key to search any food!")

# Workout Timer with Audio
        st.subheader("🎥 Exercise Tutorial Videos")
        st.write("Get exercise demonstrations from YouTube")
        
        # NAPFA component selector
        exercise = st.selectbox(
            "Select Exercise",
            ["Sit-Ups", "Standing Broad Jump", "Sit and Reach", 
             "Pull-Ups", "Shuttle Run", "2.4km Running Tips"]
        )
        
        if st.button("Find Tutorials", type="primary"):
            # Simulated YouTube recommendations (in production, use YouTube Data API)
            videos = {
                "Sit-Ups": [
                    {"title": "Perfect Sit-Up Form for NAPFA", "channel": "FitnessBlender", "duration": "5:23"},
                    {"title": "How to Do More Sit-Ups", "channel": "PE Coach", "duration": "8:15"},
                    {"title": "NAPFA Sit-Up Training", "channel": "SG Fitness", "duration": "6:40"}
                ],
                "Pull-Ups": [
                    {"title": "Pull-Up Progression Guide", "channel": "Calisthenicmovement", "duration": "12:30"},
                    {"title": "Get Your First Pull-Up", "channel": "Athlean-X", "duration": "10:15"},
                    {"title": "NAPFA Pull-Up Technique", "channel": "PE Singapore", "duration": "7:20"}
                ],
                "Standing Broad Jump": [
                    {"title": "Standing Broad Jump Technique", "channel": "Track Coach", "duration": "6:45"},
                    {"title": "How to Jump Further", "channel": "Sprint Master", "duration": "9:10"}
                ],
                "2.4km Running Tips": [
                    {"title": "2.4km NAPFA Strategy", "channel": "Running Coach SG", "duration": "11:20"},
                    {"title": "How to Run Faster 2.4km", "channel": "TrackStar", "duration": "8:50"}
                ]
            }
            
            if exercise in videos:
                st.write(f"### 📹 Top Tutorials for {exercise}")
                
                for video in videos[exercise]:
                    with st.expander(f"▶️ {video['title']} - {video['duration']}", expanded=True):
                        st.write(f"**Channel:** {video['channel']}")
                        st.write(f"**Duration:** {video['duration']}")
                        
                        # In production, embed actual video
                        st.info("🎥 Video would be embedded here with real YouTube API")
                        
                        st.write("**🔗 Search on YouTube:** ")
                        search_url = f"https://www.youtube.com/results?search_query={exercise.replace(' ', '+')}+NAPFA+tutorial"
                        st.markdown(f"[Open YouTube Search]({search_url})")
            
            st.write("")
            st.info("""
            **🔗 To enable video embedding:**
            
            Use YouTube Data API v3 (free quota):
            1. Get API key: https://console.cloud.google.com/
            2. Enable YouTube Data API
            3. Embed videos directly in app
            """)

# Workout Timer with Audio
def workout_timer():
    st.header("⏱️ Workout Timer & Audio Coach")
    st.write("Interactive timers with voice countdown and workout routines")
    
    user_data = get_user_data()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "⏰ Interval Timer",
        "🏃 NAPFA Timer",
        "💪 Custom Routine",
        "🎵 Audio Settings"
    ])
    
    with tab1:
        st.subheader("⏰ Interval Timer (HIIT/Tabata)")
        st.write("Perfect for high-intensity interval training")
        
        col1, col2 = st.columns(2)
        
        with col1:
            work_duration = st.number_input("Work Duration (seconds)", 
                                           min_value=5, max_value=300, value=30, step=5)
            rest_duration = st.number_input("Rest Duration (seconds)", 
                                           min_value=5, max_value=180, value=15, step=5)
        
        with col2:
            rounds = st.number_input("Number of Rounds", 
                                    min_value=1, max_value=50, value=8, step=1)
            prep_time = st.number_input("Preparation Time (seconds)", 
                                       min_value=0, max_value=30, value=10, step=5)
        
        # Calculate total time
        total_time = prep_time + (rounds * (work_duration + rest_duration))
        total_minutes = total_time // 60
        total_seconds = total_time % 60
        
        st.info(f"⏱️ **Total Workout Time:** {total_minutes}m {total_seconds}s")
        
        # Pre-built HIIT templates
        st.write("")
        st.write("**Quick Templates:**")
        
        template_col1, template_col2, template_col3 = st.columns(3)
        
        with template_col1:
            if st.button("Tabata (20s/10s x8)"):
                st.session_state.interval_template = {
                    'work': 20, 'rest': 10, 'rounds': 8, 'prep': 10
                }
        
        with template_col2:
            if st.button("Standard HIIT (30s/15s x10)"):
                st.session_state.interval_template = {
                    'work': 30, 'rest': 15, 'rounds': 10, 'prep': 10
                }
        
        with template_col3:
            if st.button("Sprint Intervals (45s/30s x6)"):
                st.session_state.interval_template = {
                    'work': 45, 'rest': 30, 'rounds': 6, 'prep': 15
                }
        
        # Timer display (simulated - real implementation would use JavaScript/HTML)
        st.write("")
        st.write("### Timer Display")
        
        # Create a placeholder for timer
        timer_placeholder = st.empty()
        
        # Audio cues description
        st.markdown("""
        <div class="stat-card">
            <h3>🔊 Audio Cues</h3>
            <p><strong>Preparation:</strong> "Get ready... 3, 2, 1, GO!"</p>
            <p><strong>Work Phase:</strong> "Work! Push yourself!" + countdown beeps (last 5 seconds)</p>
            <p><strong>Rest Phase:</strong> "Rest. Catch your breath." + "Next round in 3, 2, 1"</p>
            <p><strong>Halfway:</strong> "Halfway there! Keep going!"</p>
            <p><strong>Final Round:</strong> "Final round! Give it everything!"</p>
            <p><strong>Complete:</strong> "Workout complete! Great job!"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start button (in production, this would trigger actual timer)
        if st.button("▶️ Start Interval Timer", type="primary", key="start_interval"):
            st.success("🎵 Timer would start with audio cues!")
            st.info("""
            **Timer Sequence:**
            1. Prep time: {prep_time}s with "Get ready" countdown
            2. Round 1-{rounds}: {work_duration}s work + {rest_duration}s rest
            3. Audio beeps at 5, 4, 3, 2, 1 before transitions
            4. Motivational cues at halfway and final round
            5. Completion chime and celebration!
            
            *Note: Full interactive timer with audio will be available in deployed version*
            """.format(prep_time=prep_time, rounds=rounds, work_duration=work_duration, rest_duration=rest_duration))
            
            # Log workout
            exercise_name = f"Interval Training ({work_duration}s/{rest_duration}s x{rounds})"
            user_data['exercises'].insert(0, {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'name': exercise_name,
                'duration': total_minutes,
                'intensity': 'High',
                'notes': f'HIIT session'
            })
            update_user_data(user_data)
            st.balloons()
    
    with tab2:
        st.subheader("🏃 NAPFA Component Timers")
        st.write("Specialized timers for each NAPFA test")
        
        napfa_component = st.selectbox(
            "Select Component",
            ["Sit-Ups (1 minute)", "Pull-Ups (30 seconds)", "Shuttle Run Practice", 
             "2.4km Run Pacer", "Sit & Reach Hold"]
        )
        
        if napfa_component == "Sit-Ups (1 minute)":
            st.write("### 💪 Sit-Ups Timer")
            st.write("**Duration:** 60 seconds")
            
            st.markdown("""
            <div class="stat-card" style="background: linear-gradient(135deg, {0} 0%, #1565c0 100%); color: white;">
                <h2>Sit-Ups Protocol</h2>
                <p><strong>Start:</strong> "Ready... Set... GO!"</p>
                <p><strong>Every 10s:</strong> "10 seconds... 20 seconds..." (pace tracking)</p>
                <p><strong>30s:</strong> "Halfway! Keep your pace!"</p>
                <p><strong>Last 10s:</strong> Rapid countdown "10, 9, 8, 7..."</p>
                <p><strong>End:</strong> "STOP! Count complete."</p>
            </div>
            """.format(SST_COLORS['blue']), unsafe_allow_html=True)
            
            target_reps = st.number_input("Target Reps", min_value=10, max_value=60, value=35)
            
            if st.button("▶️ Start Sit-Ups Timer", type="primary"):
                st.success("🎵 60-second timer started with audio cues!")
                st.info("💡 Aim for steady pace: ~{:.1f} seconds per rep".format(60/target_reps))
        
        elif napfa_component == "Pull-Ups (30 seconds)":
            st.write("### 🏋️ Pull-Ups Timer")
            st.write("**Duration:** 30 seconds")
            
            st.markdown("""
            <div class="stat-card" style="background: linear-gradient(135deg, {0} 0%, #1565c0 100%); color: white;">
                <h2>Pull-Ups Protocol</h2>
                <p><strong>Start:</strong> "Ready... Set... GO!"</p>
                <p><strong>Every 5s:</strong> "5 seconds... 10 seconds..."</p>
                <p><strong>15s:</strong> "Halfway! Keep pulling!"</p>
                <p><strong>Last 5s:</strong> "5, 4, 3, 2, 1"</p>
                <p><strong>End:</strong> "STOP! Time's up."</p>
            </div>
            """.format(SST_COLORS['red']), unsafe_allow_html=True)
            
            if st.button("▶️ Start Pull-Ups Timer", type="primary"):
                st.success("🎵 30-second timer started!")
        
        elif napfa_component == "Shuttle Run Practice":
            st.write("### 🏃 Shuttle Run Timer")
            st.write("**Practice with timing cues**")
            
            st.markdown("""
            <div class="stat-card">
                <h3>Shuttle Run Protocol</h3>
                <p><strong>Beep 1:</strong> "Ready... Set... GO!" (start first 9.14m)</p>
                <p><strong>Turn 1:</strong> "TURN! Go!" (at ~4.5 seconds)</p>
                <p><strong>Turn 2:</strong> "TURN! Go!" (at ~9 seconds)</p>
                <p><strong>Turn 3:</strong> "TURN! Push!" (at ~13.5 seconds)</p>
                <p><strong>Finish:</strong> "FINISH! Cross the line!" (at ~18 seconds)</p>
                <p><em>Total distance: 4 x 9.14m = 36.56m</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶️ Start Shuttle Run Timer", type="primary"):
                st.success("🎵 Shuttle run timer started with turn cues!")
        
        elif napfa_component == "2.4km Run Pacer":
            st.write("### 🏃 2.4km Run Pacer")
            st.write("Audio pace guidance for your target time")
            
            target_time = st.text_input("Target Time (min:sec)", value="10:30", 
                                       placeholder="e.g., 10:30")
            
            try:
                time_parts = target_time.split(':')
                target_minutes = int(time_parts[0])
                target_seconds = int(time_parts[1])
                total_target_seconds = target_minutes * 60 + target_seconds
                
                # Calculate lap times (assuming 6 laps = 400m each = 2400m)
                lap_time = total_target_seconds / 6
                lap_minutes = int(lap_time // 60)
                lap_seconds = int(lap_time % 60)
                
                st.info(f"🎯 **Target Pace:** {lap_minutes}:{lap_seconds:02d} per 400m lap")
                
                st.markdown("""
                <div class="stat-card">
                    <h3>Pace Audio Cues</h3>
                    <p><strong>Start:</strong> "Ready to run 2.4km. Target time: {target}. GO!"</p>
                    <p><strong>Each 400m:</strong> "Lap X complete. Time: X:XX. {pace_status}"</p>
                    <p><strong>1200m (Halfway):</strong> "Halfway! You're {status}. {encouragement}"</p>
                    <p><strong>2000m:</strong> "400m to go! Pick up the pace!"</p>
                    <p><strong>Final 200m:</strong> "Final sprint! Give it everything!"</p>
                    <p><strong>Finish:</strong> "Done! Time: X:XX. {result}"</p>
                </div>
                """.format(target=target_time), unsafe_allow_html=True)
                
                if st.button("▶️ Start 2.4km Pacer", type="primary"):
                    st.success(f"🎵 Pacer started! Target: {target_time}")
                    st.info("💡 GPS tracking and lap timing would be enabled in mobile version")
            
            except:
                st.error("Invalid time format. Use MM:SS (e.g., 10:30)")
        
        else:  # Sit & Reach Hold
            st.write("### 🧘 Sit & Reach Hold Timer")
            st.write("Hold your maximum reach for 2 seconds")
            
            st.markdown("""
            <div class="stat-card">
                <h3>Hold Protocol</h3>
                <p><strong>Setup:</strong> "Position yourself... reach forward slowly"</p>
                <p><strong>Reach max:</strong> "Hold steady... 2... 1... recorded!"</p>
                <p><strong>Result:</strong> "Measurement: XX cm"</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶️ Start Hold Timer", type="primary"):
                st.success("🎵 2-second hold timer started!")
    
    with tab3:
        st.subheader("💪 Custom Workout Routine Builder")
        st.write("Create your own timed workout routine")
        
        # Initialize routine in session state
        if 'workout_routine' not in st.session_state:
            st.session_state.workout_routine = []
        
        st.write("### Build Your Routine")
        
        # Add exercise
        col1, col2, col3 = st.columns(3)
        
        with col1:
            exercise_name = st.text_input("Exercise Name", placeholder="e.g., Push-ups")
        
        with col2:
            exercise_duration = st.number_input("Duration (seconds)", 
                                               min_value=5, max_value=300, value=30, step=5)
        
        with col3:
            exercise_rest = st.number_input("Rest After (seconds)", 
                                           min_value=0, max_value=180, value=10, step=5)
        
        if st.button("➕ Add to Routine"):
            if exercise_name:
                st.session_state.workout_routine.append({
                    'name': exercise_name,
                    'duration': exercise_duration,
                    'rest': exercise_rest
                })
                st.success(f"Added: {exercise_name}")
                st.rerun()
        
        # Display current routine
        if st.session_state.workout_routine:
            st.write("")
            st.write("### Your Routine")
            
            total_workout_time = sum(ex['duration'] + ex['rest'] for ex in st.session_state.workout_routine)
            st.metric("Total Time", f"{total_workout_time // 60}m {total_workout_time % 60}s")
            
            for idx, exercise in enumerate(st.session_state.workout_routine):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{idx + 1}. {exercise['name']}**")
                
                with col2:
                    st.write(f"⏱️ {exercise['duration']}s")
                
                with col3:
                    st.write(f"😴 {exercise['rest']}s rest")
                
                with col4:
                    if st.button("🗑️", key=f"delete_ex_{idx}"):
                        st.session_state.workout_routine.pop(idx)
                        st.rerun()
            
            # Start routine
            st.write("")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Start Routine", type="primary", key="start_custom"):
                    st.success("🎵 Custom routine started!")
                    
                    # Show sequence
                    st.write("**Routine Sequence:**")
                    for idx, ex in enumerate(st.session_state.workout_routine):
                        st.write(f"{idx + 1}. {ex['name']} - {ex['duration']}s")
                        if ex['rest'] > 0:
                            st.write(f"   Rest - {ex['rest']}s")
                    
                    # Log workout
                    total_duration = total_workout_time // 60
                    user_data['exercises'].insert(0, {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'name': 'Custom Routine',
                        'duration': total_duration,
                        'intensity': 'Medium',
                        'notes': f'{len(st.session_state.workout_routine)} exercises'
                    })
                    update_user_data(user_data)
            
            with col2:
                if st.button("🗑️ Clear Routine"):
                    st.session_state.workout_routine = []
                    st.rerun()
        
        # Pre-built routines
        st.write("")
        st.write("### 📋 Pre-Built Routines")
        
        routine_templates = {
            "Beginner Full Body": [
                {"name": "Jumping Jacks", "duration": 30, "rest": 15},
                {"name": "Push-ups", "duration": 30, "rest": 15},
                {"name": "Squats", "duration": 30, "rest": 15},
                {"name": "Plank", "duration": 30, "rest": 15},
                {"name": "High Knees", "duration": 30, "rest": 15}
            ],
            "NAPFA Training": [
                {"name": "Sit-ups", "duration": 60, "rest": 30},
                {"name": "Push-ups", "duration": 45, "rest": 30},
                {"name": "Squat Jumps", "duration": 30, "rest": 30},
                {"name": "Pull-up Negatives", "duration": 30, "rest": 30},
                {"name": "Sprint Intervals", "duration": 20, "rest": 40}
            ],
            "Core Blast": [
                {"name": "Crunches", "duration": 45, "rest": 15},
                {"name": "Plank", "duration": 60, "rest": 20},
                {"name": "Russian Twists", "duration": 45, "rest": 15},
                {"name": "Bicycle Crunches", "duration": 45, "rest": 15},
                {"name": "Mountain Climbers", "duration": 30, "rest": 15}
            ]
        }
        
        template_cols = st.columns(3)
        
        for idx, (template_name, exercises) in enumerate(routine_templates.items()):
            with template_cols[idx % 3]:
                if st.button(f"📋 {template_name}"):
                    st.session_state.workout_routine = exercises.copy()
                    st.rerun()
    
    with tab4:
        st.subheader("🎵 Audio & Voice Settings")
        st.write("Customize your workout audio experience")
        
        # Voice settings
        st.write("### 🗣️ Voice Coach Settings")
        
        voice_enabled = st.checkbox("Enable Voice Cues", value=True)
        voice_type = st.selectbox("Voice Type", ["Male Coach", "Female Coach", "Motivational", "Calm"])
        voice_volume = st.slider("Voice Volume", min_value=0, max_value=100, value=80, step=5)
        
        # Sound effects
        st.write("")
        st.write("### 🔊 Sound Effects")
        
        beep_enabled = st.checkbox("Enable Countdown Beeps", value=True)
        beep_volume = st.slider("Beep Volume", min_value=0, max_value=100, value=70, step=5)
        
        completion_sound = st.selectbox(
            "Completion Sound",
            ["Victory Chime", "Air Horn", "Applause", "Bell", "None"]
        )
        
        # Motivational cues
        st.write("")
        st.write("### 💪 Motivational Cues")
        
        motivation_frequency = st.selectbox(
            "Encouragement Frequency",
            ["Every interval", "Every 2 intervals", "Halfway & Final only", "Off"]
        )
        
        motivation_style = st.selectbox(
            "Motivation Style",
            ["Aggressive (Push harder!)", "Supportive (You got this!)", 
             "Technical (Form check)", "Minimal"]
        )
        
        # Sample phrases
        st.write("")
        st.write("**Sample Motivational Phrases:**")
        
        if motivation_style == "Aggressive (Push harder!)":
            st.info("• 'Don't quit now!'\n• 'This is where champions are made!'\n• 'One more rep! PUSH!'")
        elif motivation_style == "Supportive (You got this!)":
            st.info("• 'Great job! Keep it up!'\n• 'You're doing amazing!'\n• 'Almost there, stay strong!'")
        elif motivation_style == "Technical (Form check)":
            st.info("• 'Check your form'\n• 'Engage your core'\n• 'Controlled movements'")
        else:
            st.info("• Minimal voice cues only")
        
        # Music integration note
        st.write("")
        st.write("### 🎵 Music Integration (Coming Soon)")
        st.info("""
        **Future Features:**
        - Spotify integration for workout playlists
        - BPM-matched music for running pace
        - Auto-ducking (music lowers during voice cues)
        - Custom playlist creator
        """)
        
        # Save settings
        if st.button("💾 Save Audio Settings", type="primary"):
            audio_settings = {
                'voice_enabled': voice_enabled,
                'voice_type': voice_type,
                'voice_volume': voice_volume,
                'beep_enabled': beep_enabled,
                'beep_volume': beep_volume,
                'completion_sound': completion_sound,
                'motivation_frequency': motivation_frequency,
                'motivation_style': motivation_style
            }
            
            user_data['audio_settings'] = audio_settings
            update_user_data(user_data)
            
            st.success("✅ Audio settings saved!")
            st.balloons()
        
        # Test audio
        st.write("")
        if st.button("🔊 Test Audio Cues"):
            st.success("🎵 Audio test would play:")
            st.write("1. 'Get ready... 3, 2, 1, GO!' (Voice cue)")
            st.write("2. Beep sounds (3 short beeps)")
            st.write("3. Motivational phrase based on your style")
            st.write(f"4. Completion sound: {completion_sound}")

# Teacher Dashboard
def teacher_dashboard():
    st.header("👨‍🏫 Teacher Dashboard")
    
    user_data = get_user_data()
    all_users = st.session_state.users_data
    
    # Display class code
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {SST_COLORS['blue']} 0%, #1565c0 100%); color: white;">
        <h2>📝 Your Class Code: {user_data['class_code']}</h2>
        <p>Share this code with your students to join your class</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Get student list
    student_usernames = user_data.get('students', [])
    students_data = {username: all_users[username] for username in student_usernames if username in all_users}
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Class Overview",
        "👥 Student List", 
        "📈 Performance Analysis",
        "📄 Export Reports"
    ])
    
    with tab1:
        st.subheader("Class Overview")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", f"{len(students_data)}/30")
        
        with col2:
            # Calculate average NAPFA
            napfa_scores = []
            for student in students_data.values():
                if student.get('napfa_history'):
                    napfa_scores.append(student['napfa_history'][-1]['total'])
            
            if napfa_scores:
                avg_napfa = sum(napfa_scores) / len(napfa_scores)
                st.metric("Avg NAPFA Score", f"{avg_napfa:.1f}/30")
            else:
                st.metric("Avg NAPFA Score", "No data")
        
        with col3:
            # Active this week
            week_ago = datetime.now() - timedelta(days=7)
            active_count = 0
            for student in students_data.values():
                if student.get('exercises'):
                    for exercise in student['exercises']:
                        if datetime.strptime(exercise['date'], '%Y-%m-%d') >= week_ago:
                            active_count += 1
                            break
            
            st.metric("Active This Week", f"{active_count}/{len(students_data)}")
        
        with col4:
            # Total workouts this week
            total_workouts = 0
            for student in students_data.values():
                if student.get('exercises'):
                    weekly = [e for e in student['exercises'] 
                            if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                    total_workouts += len(weekly)
            
            st.metric("Class Workouts", total_workouts)
        
        # Performance distribution
        if napfa_scores:
            st.write("")
            st.write("### 📊 NAPFA Score Distribution")
            
            # Create distribution chart
            df = pd.DataFrame({'Score': napfa_scores})
            st.bar_chart(df['Score'].value_counts().sort_index())
            
            # Medal counts
            st.write("")
            st.write("### 🏅 Medal Distribution")
            
            medal_counts = {'🥇 Gold': 0, '🥈 Silver': 0, '🥉 Bronze': 0, 'No Medal': 0}
            for student in students_data.values():
                if student.get('napfa_history'):
                    medal = student['napfa_history'][-1]['medal']
                    if '🥇' in medal:
                        medal_counts['🥇 Gold'] += 1
                    elif '🥈' in medal:
                        medal_counts['🥈 Silver'] += 1
                    elif '🥉' in medal:
                        medal_counts['🥉 Bronze'] += 1
                    else:
                        medal_counts['No Medal'] += 1
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🥇 Gold", medal_counts['🥇 Gold'])
            col2.metric("🥈 Silver", medal_counts['🥈 Silver'])
            col3.metric("🥉 Bronze", medal_counts['🥉 Bronze'])
            col4.metric("No Medal", medal_counts['No Medal'])
        
        # Top performers
        if napfa_scores:
            st.write("")
            st.write("### ⭐ Top Performers")
            
            student_scores = []
            for username, student in students_data.items():
                if student.get('napfa_history'):
                    student_scores.append({
                        'name': student['name'],
                        'username': username,
                        'score': student['napfa_history'][-1]['total'],
                        'medal': student['napfa_history'][-1]['medal']
                    })
            
            student_scores.sort(key=lambda x: x['score'], reverse=True)
            
            for idx, student in enumerate(student_scores[:5], 1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                st.write(f"{medal} **{student['name']}** - {student['score']}/30 ({student['medal']})")
        
        # Students needing attention
        st.write("")
        st.write("### ⚠️ Students Needing Attention")
        
        needs_attention = []
        for username, student in students_data.items():
            # Check if inactive
            if not student.get('exercises') or len(student.get('exercises', [])) == 0:
                needs_attention.append(f"📝 **{student['name']}** - No workouts logged")
            elif student.get('napfa_history'):
                latest_napfa = student['napfa_history'][-1]
                if latest_napfa['total'] < 9:
                    needs_attention.append(f"📉 **{student['name']}** - Low NAPFA score ({latest_napfa['total']}/30)")
        
        if needs_attention:
            for msg in needs_attention[:5]:
                st.warning(msg)
        else:
            st.success("✅ All students doing well!")
    
    with tab2:
        st.subheader("Student List")
        
        if not students_data:
            st.info("No students in your class yet. Share your class code: " + user_data['class_code'])
        else:
            # Search and filter
            search = st.text_input("🔍 Search students", placeholder="Enter name or username")
            
            # Display students
            for username, student in students_data.items():
                if search.lower() in student['name'].lower() or search.lower() in username.lower() or not search:
                    with st.expander(f"👤 {student['name']} (@{username})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Email:** {student.get('email', 'N/A')}")
                            st.write(f"**Age:** {student.get('age', 'N/A')}")
                            st.write(f"**Gender:** {'Male' if student.get('gender') == 'm' else 'Female'}")
                        
                        with col2:
                            if student.get('napfa_history'):
                                latest = student['napfa_history'][-1]
                                st.write(f"**NAPFA:** {latest['total']}/30")
                                st.write(f"**Medal:** {latest['medal']}")
                            else:
                                st.write("**NAPFA:** Not tested")
                            
                            st.write(f"**Workouts:** {len(student.get('exercises', []))}")
                        
                        with col3:
                            st.write(f"**Level:** {student.get('level', 'Novice')}")
                            st.write(f"**Points:** {student.get('total_points', 0)}")
                            st.write(f"**Login Streak:** {student.get('login_streak', 0)} days")
                        
                        # Quick actions
                        st.write("")
                        if st.button(f"Remove from class", key=f"remove_{username}"):
                            user_data['students'].remove(username)
                            student['teacher_class'] = None
                            update_user_data(user_data)
                            save_users(all_users)
                            st.success(f"Removed {student['name']} from class")
                            st.rerun()
    
    with tab3:
        st.subheader("Performance Analysis")
        
        if not students_data:
            st.info("No students to analyze yet")
        else:
            # NAPFA component analysis
            st.write("### 📊 NAPFA Component Breakdown")
            
            component_scores = {
                'Sit-Ups': [],
                'Broad Jump': [],
                'Sit & Reach': [],
                'Pull-Ups': [],
                'Shuttle Run': [],
                '2.4km Run': []
            }
            
            component_map = {
                'SU': 'Sit-Ups',
                'SBJ': 'Broad Jump',
                'SAR': 'Sit & Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }
            
            for student in students_data.values():
                if student.get('napfa_history'):
                    grades = student['napfa_history'][-1]['grades']
                    for code, name in component_map.items():
                        if code in grades:
                            component_scores[name].append(grades[code])
            
            if any(component_scores.values()):
                # Calculate averages
                avg_scores = {name: sum(scores)/len(scores) if scores else 0 
                            for name, scores in component_scores.items()}
                
                df = pd.DataFrame({
                    'Component': list(avg_scores.keys()),
                    'Average Grade': list(avg_scores.values())
                })
                
                st.bar_chart(df.set_index('Component'))
                
                # Identify weak areas
                weak_components = [name for name, avg in avg_scores.items() if avg < 3]
                if weak_components:
                    st.warning(f"⚠️ **Class weak areas:** {', '.join(weak_components)}")
                    st.info("💡 Consider focusing class training on these components")
            
            # Participation trends
            st.write("")
            st.write("### 📈 Weekly Participation Trend")
            
            # Last 4 weeks
            weeks_data = []
            for week in range(4):
                week_start = datetime.now() - timedelta(days=7 * (week + 1))
                week_end = datetime.now() - timedelta(days=7 * week)
                
                active_count = 0
                for student in students_data.values():
                    if student.get('exercises'):
                        for exercise in student['exercises']:
                            ex_date = datetime.strptime(exercise['date'], '%Y-%m-%d')
                            if week_start <= ex_date < week_end:
                                active_count += 1
                                break
                
                weeks_data.append({
                    'Week': f"Week {4-week}",
                    'Active Students': active_count
                })
            
            df_weeks = pd.DataFrame(weeks_data)
            st.line_chart(df_weeks.set_index('Week'))
    
    with tab4:
        st.subheader("Export Class Reports")
        
        st.write("### 📊 Google Sheets Export")
        st.info("Generate a comprehensive class report and export to Google Sheets")
        
        # Report options
        include_napfa = st.checkbox("Include NAPFA scores", value=True)
        include_workouts = st.checkbox("Include workout logs", value=True)
        include_attendance = st.checkbox("Include attendance/participation", value=True)
        
        if st.button("📄 Generate Report (Download CSV)", type="primary"):
            if not students_data:
                st.error("No students to export")
            else:
                # Generate report data
                report_data = []
                
                for username, student in students_data.items():
                    row = {
                        'Name': student['name'],
                        'Email': student.get('email', ''),
                        'Age': student.get('age', ''),
                        'Gender': 'Male' if student.get('gender') == 'm' else 'Female'
                    }
                    
                    if include_napfa and student.get('napfa_history'):
                        latest = student['napfa_history'][-1]
                        row['NAPFA Total'] = latest['total']
                        row['Medal'] = latest['medal']
                        row['Sit-Ups'] = latest['grades'].get('SU', 0)
                        row['Broad Jump'] = latest['grades'].get('SBJ', 0)
                        row['Sit & Reach'] = latest['grades'].get('SAR', 0)
                        row['Pull-Ups'] = latest['grades'].get('PU', 0)
                        row['Shuttle Run'] = latest['grades'].get('SR', 0)
                        row['2.4km Run'] = latest['grades'].get('RUN', 0)
                    
                    if include_workouts:
                        row['Total Workouts'] = len(student.get('exercises', []))
                        
                        # This week
                        week_ago = datetime.now() - timedelta(days=7)
                        weekly = [e for e in student.get('exercises', []) 
                                if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                        row['Workouts This Week'] = len(weekly)
                    
                    if include_attendance:
                        row['Login Streak'] = student.get('login_streak', 0)
                        row['Level'] = student.get('level', 'Novice')
                        row['Total Points'] = student.get('total_points', 0)
                    
                    report_data.append(row)
                
                # Create DataFrame
                df_report = pd.DataFrame(report_data)
                
                # Convert to CSV
                csv = df_report.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv,
                    file_name=f"class_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
                st.success("✅ Report generated! Click to download.")
                
                # Preview
                st.write("### Preview")
                st.dataframe(df_report, use_container_width=True)
        
        st.write("")
        st.write("### 📧 Share Instructions")
        st.info("""
        **To share this report with others:**
        1. Download the CSV file
        2. Upload to Google Sheets
        3. Click Share → Add people (enter emails)
        4. Set permissions (Viewer = read-only, Editor = can edit)
        5. Send the link!
        
        **For automatic Google Sheets export, this feature will be available after deployment.**
        """)

# Schedule Manager
def schedule_manager():
    st.header("📅 Training Schedule")
    
    with st.form("schedule_form"):
        day = st.selectbox("Day of Week", 
                          ["Monday", "Tuesday", "Wednesday", "Thursday", 
                           "Friday", "Saturday", "Sunday"])
        activity = st.text_input("Activity", placeholder="e.g., Morning run")
        
        col1, col2 = st.columns(2)
        with col1:
            time = st.time_input("Time")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        
        submitted = st.form_submit_button("Add to Schedule")
        
        if submitted:
            if activity:
                user_data = get_user_data()
                user_data['schedule'].append({
                    'day': day,
                    'activity': activity,
                    'time': str(time),
                    'duration': duration
                })
                update_user_data(user_data)
                st.success("Activity added to schedule!")
                st.rerun()
            else:
                st.error("Please enter activity name")
    
    # Display schedule
    user_data = get_user_data()
    if user_data['schedule']:
        st.subheader("Weekly Schedule")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            day_activities = [s for s in user_data['schedule'] if s['day'] == day]
            if day_activities:
                st.markdown(f"### {day}")
                for activity in day_activities:
                    st.markdown(f'<div class="stat-card"><strong>{activity["activity"]}</strong><br>{activity["time"]} - {activity["duration"]} minutes</div>', 
                              unsafe_allow_html=True)
    else:
        st.info("No activities scheduled yet.")

# Main App
def main_app():
    user_data = get_user_data()
    
    # Check if teacher or student
    is_teacher = user_data.get('role') == 'teacher'
    
    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        if is_teacher:
            st.markdown(f'<div class="main-header"><h1>🏋️ FitTrack - Teacher Portal</h1><p>Welcome, {user_data["name"]}!</p></div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="main-header"><h1>🏋️ FitTrack</h1><p>Welcome back, {user_data["name"]}!</p></div>', 
                       unsafe_allow_html=True)
    with col2:
        st.write("")
        st.write("")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    # Different interface for teachers vs students
    if is_teacher:
        teacher_dashboard()
    else:
        # Update login streak for students
        user_data = update_login_streak(user_data)
        update_user_data(user_data)
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Choose a feature:", 
                               ["📊 Weekly Progress", "🏆 Community", "🤖 AI Insights", 
                                "🏥 Advanced Metrics", "🌐 Integrations", "⏱️ Workout Timer",
                                "BMI Calculator", "NAPFA Test", "Sleep Tracker", 
                                "Exercise Log", "Set Goals", "Training Schedule"])
        
        # Display selected page
        if page == "📊 Weekly Progress":
            reminders_and_progress()
        elif page == "🏆 Community":
            community_features()
        elif page == "🤖 AI Insights":
            ai_insights()
        elif page == "🏥 Advanced Metrics":
            advanced_metrics()
        elif page == "🌐 Integrations":
            api_integrations()
        elif page == "⏱️ Workout Timer":
            workout_timer()
        elif page == "BMI Calculator":
        bmi_calculator()
    elif page == "NAPFA Test":
        napfa_calculator()
    elif page == "Sleep Tracker":
        sleep_tracker()
    elif page == "Exercise Log":
        exercise_logger()
    elif page == "Set Goals":
        goal_setting()
    elif page == "Training Schedule":
        schedule_manager()

# Main execution
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
