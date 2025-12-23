import asyncio
import random
from app.services.analytics_service import analytics_service

# Simulation Configuration
NUM_USERS = 5
NUM_QUESTIONS = 20
SKILL_ID = "Math.Algebra.Quadratics"

class UserSim:
    def __init__(self, user_id, initial_mastery):
        self.user_id = user_id
        self.mastery = initial_mastery # True latent mastery probability
        self.bkt_state = 0.1 # System's belief of mastery (starts low)

    def attempt_question(self):
        # Simulate answering based on true mastery
        # Simple probabilistic model: P(Correct) = Mastery * (1-Slip) + (1-Mastery) * Guess
        p_slip = 0.1
        p_guess = 0.2
        
        p_correct = self.mastery * (1 - p_slip) + (1 - self.mastery) * p_guess
        is_correct = random.random() < p_correct
        return is_correct

    def learn(self):
        # User actually learns a bit after each attempt
        self.mastery = min(1.0, self.mastery + 0.05)

async def run_simulation():
    print(f"--- Starting Learning Simulation for Skill: {SKILL_ID} ---")
    print(f"Params: {NUM_USERS} Users, {NUM_QUESTIONS} Questions each")
    
    users = [UserSim(f"User_{i}", initial_mastery=random.uniform(0.1, 0.4)) for i in range(NUM_USERS)]
    
    for step in range(NUM_QUESTIONS):
        print(f"\n[Step {step+1}]")
        for user in users:
            # 1. User attempts question
            is_correct = user.attempt_question()
            
            # 2. System updates BKT state (The complex math part)
            new_bkt = analytics_service.update_bkt(user.user_id, SKILL_ID, is_correct)
            user.bkt_state = new_bkt
            
            # 3. User learns
            user.learn()
            
            # Log
            result = "✅" if is_correct else "❌"
            print(f"  {user.user_id}: {result} | Sys Belief: {user.bkt_state:.3f} | True Mastery: {user.mastery:.3f}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
