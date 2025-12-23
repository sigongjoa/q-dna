import asyncio
import random
import json
import os
from app.services.analytics_service import analytics_service

# Configuration
NUM_STUDENTS = 25
SKILLS = ["Algebra.Linear", "Algebra.Quadratics", "Geometry.Triangles", "Geometry.Circles", "Calculus.Limits"]

# Student Archetypes
ARCHETYPES = [
    {"name": "Fast Learner", "init": (0.3, 0.5), "learn_rate": 0.15},
    {"name": "Average Student", "init": (0.1, 0.3), "learn_rate": 0.05},
    {"name": "Struggling", "init": (0.0, 0.2), "learn_rate": 0.02},
]

class StudentSim:
    def __init__(self, student_id, archetype):
        self.student_id = student_id
        self.archetype = archetype
        # True Mastery per skill
        self.true_mastery = {skill: random.uniform(*archetype["init"]) for skill in SKILLS}
        # System Belief (BKT) per skill
        self.sys_mastery = {skill: 0.1 for skill in SKILLS} # Initial prior

    def attempt(self, skill):
        # Probabilistic attempt
        mastery = self.true_mastery[skill]
        p_slip = 0.1
        p_guess = 0.2
        p_correct = mastery * (1 - p_slip) + (1 - mastery) * p_guess
        return random.random() < p_correct

    def learn(self, skill):
        # Learn based on rate
        rate = self.archetype["learn_rate"] * random.uniform(0.8, 1.2)
        self.true_mastery[skill] = min(0.99, self.true_mastery[skill] + rate)

async def run_simulation():
    print(f"--- Generating Real-World Learning Data ({NUM_STUDENTS} Students, {len(SKILLS)} Skills) ---")
    
    students = []
    for i in range(NUM_STUDENTS):
        arch = random.choice(ARCHETYPES)
        students.append(StudentSim(f"Student {i+1}", arch))

    # Simulate 50 questions per student (randomly distributed across skills)
    for step in range(50):
        for student in students:
            # Pick a random skill to practice
            skill = random.choice(SKILLS)
            
            # Attempt
            is_correct = student.attempt(skill)
            
            # System Analysis (BKT Update)
            # In a real app we'd fetch previous state from DB, here we keep in memory
            # We assume analytics_service is stateless utility for the formula
            # But wait, our update_bkt in service *returns* the new value, it doesn't store state in this mock context unless we changed it.
            # actually our service mock implementation in previous turn used a hardcoded p_L = 0.3. 
            # We should probably update the service calculation to take 'current_belief' as arg for simulation purposes, 
            # OR just implement the BKT logic here correctly for the simulation data generation.
            # Let's implement BKT logic here locally to ensure high quality data.
            
            prior = student.sys_mastery[skill]
            p_S = 0.1
            p_G = 0.2
            p_T = 0.1
            
            if is_correct:
                num = prior * (1 - p_S)
                denom = num + (1 - prior) * p_G
                posterior = num / (denom + 1e-9)
            else:
                num = prior * p_S
                denom = num + (1 - prior) * (1 - p_G)
                posterior = num / (denom + 1e-9)
            
            student.sys_mastery[skill] = posterior + (1 - posterior) * p_T

            # Student actually learns
            student.learn(skill)

    # Format Data for Frontend Nivo Heatmap
    # Format: [ { "id": "Student 1", "data": [ {"x": "Algebra", "y": 80}, ... ] }, ... ]
    
    heatmap_data = []
    for s in students:
        datapoints = []
        for skill in SKILLS:
            # Convert 0.0-1.0 to 0-100 score
            score = int(s.sys_mastery[skill] * 100)
            datapoints.append({"x": skill, "y": score})
        
        heatmap_data.append({
            "id": s.student_id,
            "data": datapoints
        })

    # Save to file reachable by Frontend
    output_path = "../frontend/src/data/simulation_results.json"
    with open(output_path, "w") as f:
        json.dump(heatmap_data, f, indent=2)
    
    print(f"Analysis Complete. Data exported to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
