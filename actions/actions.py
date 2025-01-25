from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

class ActionSetActiveCollege(Action):
    def name(self) -> Text:
        return "action_set_active_college"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        
        # Enhanced college mappings with more keywords
        college_keywords = {
            'ccs': ['ccs', 'computer', 'computing', 'it', 'information technology', 'programming'],
            'coe': ['coe', 'engineering', 'engineer'],
            'csm': ['csm', 'science', 'math', 'mathematics'],
            'cbaa': ['cbaa', 'business', 'accountancy', 'accounting'],
            'cass': ['cass', 'arts', 'social sciences', 'sociology'],
            'ced': ['ced', 'education', 'teaching'],
            'chs': ['chs', 'health', 'nursing']
        }

        # Get current context
        current_college = tracker.get_slot('active_college')
        current_topic = tracker.get_slot('active_topic')
        
        # Determine new college from message
        new_college = None
        for college, keywords in college_keywords.items():
            if any(keyword in message for keyword in keywords):
                new_college = college
                break

        events = []
        if new_college:
            # If switching colleges, track the change
            if current_college and new_college != current_college:
                events.append(SlotSet("last_topic", current_college))
                events.append(SlotSet("conversation_stage", "switching"))
            
            events.extend([
                SlotSet("active_college", new_college),
                SlotSet("active_topic", f"{new_college}_general")
            ])
        
        return events

class ActionHandleContextSwitch(Action):
    def name(self) -> Text:
        return "action_handle_context_switch"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        active_college = tracker.get_slot('active_college')
        last_topic = tracker.get_slot('last_topic')
        conversation_stage = tracker.get_slot('conversation_stage')
        
        if conversation_stage == "switching":
            if last_topic:
                # Acknowledge the topic switch
                dispatcher.utter_message(response="utter_help_refocus")
            return [SlotSet("conversation_stage", "inquiring")]
        
        return []

class ActionHandleFollowUp(Action):
    def name(self) -> Text:
        return "action_handle_follow_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        active_college = tracker.get_slot('active_college')
        active_topic = tracker.get_slot('active_topic')
        
        # Handle follow-up based on current context
        if active_college == 'ccs':
            if 'programs' in active_topic:
                dispatcher.utter_message(text="Would you like to know about:\n1. Admission requirements\n2. Course curriculum\n3. Career opportunities")
            elif 'facilities' in active_topic:
                dispatcher.utter_message(text="Would you like to know about:\n1. Laboratory equipment\n2. Research facilities\n3. Study areas")
        
        return [SlotSet("conversation_stage", "following_up")]

class ActionTrackConversation(Action):
    def name(self) -> Text:
        return "action_track_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get current state
        current_intent = tracker.latest_message.get('intent', {}).get('name')
        active_college = tracker.get_slot('active_college')
        conversation_stage = tracker.get_slot('conversation_stage')
        
        events = []
        
        # Track conversation progression
        if not conversation_stage:
            events.append(SlotSet("conversation_stage", "initial"))
        elif conversation_stage == "initial" and active_college:
            events.append(SlotSet("conversation_stage", "inquiring"))
        
        # Log conversation state for debugging
        print(f"Current Intent: {current_intent}")
        print(f"Active College: {active_college}")
        print(f"Conversation Stage: {conversation_stage}")
        
        return events
    
class ActionSmartFollowUp(Action):
    def name(self) -> Text:
        return "action_smart_follow_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_intent = tracker.latest_message.get('intent', {}).get('name')
        active_program = tracker.get_slot('program')
        active_topic = tracker.get_slot('active_topic')
        
        # Smart follow-up suggestions based on conversation context
        follow_up_map = {
            'ask_program_details': [
                'ask_program_subjects',
                'ask_program_difficulty',
                'ask_career_prospects'
            ],
            'ask_about_bsca': [
                'ask_program_subjects',
                'ask_career_prospects',
                'ask_admission_requirements'
            ],
            'ask_admission_requirements': [
                'ask_about_msu_scholarships',
                'ask_program_duration',
                'ccs_facilities'
            ]
        }
        
        if current_intent in follow_up_map:
            suggestions = follow_up_map[current_intent]
            response = "Would you like to know about:\n"
            if active_program:
                response = f"For {active_program}, would you like to know about:\n"
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion.replace('_', ' ').title()}\n"
            dispatcher.utter_message(text=response)
        
        return []

class ActionHandleProgramComparison(Action):
    def name(self) -> Text:
        return "action_handle_program_comparison"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        programs = ['bscs', 'bsit', 'bsis', 'bsca']
        
        mentioned_programs = [prog for prog in programs if prog in message]
        
        if len(mentioned_programs) >= 2:
            # Custom comparison for specifically mentioned programs
            prog1, prog2 = mentioned_programs[:2]
            dispatcher.utter_message(
                text=f"Let me compare {prog1.upper()} and {prog2.upper()} for you..."
            )
            return [
                SlotSet("active_topic", f"compare_{prog1}_{prog2}"),
                FollowupAction("utter_program_comparison")
            ]
        
        return []

class ActionTrackStudentInterest(Action):
    def name(self) -> Text:
        return "action_track_student_interest"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Track what aspects the student shows most interest in
        message = tracker.latest_message.get('text', '').lower()
        
        interest_categories = {
            'technical': ['programming', 'coding', 'development', 'software'],
            'business': ['business', 'management', 'enterprise'],
            'creative': ['design', 'ui', 'ux', 'interface'],
            'research': ['research', 'analysis', 'study']
        }
        
        interests = []
        for category, keywords in interest_categories.items():
            if any(keyword in message for keyword in keywords):
                interests.append(category)
        
        if interests:
            # Customize response based on detected interests
            program_suggestions = {
                'technical': 'BSCS or BSIT',
                'business': 'BSIS',
                'creative': 'BSCA',
                'research': 'BSCS'
            }
            
            suggestions = [program_suggestions[interest] for interest in interests]
            response = f"Based on your interests, you might want to consider {' or '.join(set(suggestions))}."
            dispatcher.utter_message(text=response)
        
        return []

class ActionHandleMultipleQuestions(Action):
    def name(self) -> Text:
        return "action_handle_multiple_questions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Handle cases where user asks multiple questions in one message
        message = tracker.latest_message.get('text', '').lower()
        
        # Question markers
        question_markers = ['how', 'what', 'where', 'when', 'who', 'why', 'can', 'does']
        questions = []
        
        # Split message into potential questions
        sentences = message.split('?')
        for sentence in sentences:
            if any(marker in sentence for marker in question_markers):
                questions.append(sentence.strip())
        
        if len(questions) > 1:
            dispatcher.utter_message(text="I noticed you have multiple questions. Let me address them one by one:")
            for i, question in enumerate(questions, 1):
                dispatcher.utter_message(text=f"{i}. Regarding '{question}'...")
        
        return []