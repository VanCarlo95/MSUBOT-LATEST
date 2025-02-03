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
        
        # Enhanced college mappings with more context-aware keywords
        college_keywords = {
            'ccs': [
                'ccs', 'computer', 'computing', 'it', 'information technology', 
                'programming', 'software', 'development', 'coding', 'cs', 
                'information systems', 'is', 'computer applications', 'ca'
            ],
            'coe': [
                'coe', 'engineering', 'engineer', 'mechanical', 'civil', 
                'electrical', 'chemical', 'industrial'
            ],
            'csm': [
                'csm', 'science', 'math', 'mathematics', 'biology', 'chemistry', 
                'physics', 'laboratory'
            ],
            'cbaa': [
                'cbaa', 'business', 'accountancy', 'accounting', 'management', 
                'finance', 'economics'
            ],
            'cass': [
                'cass', 'arts', 'social sciences', 'sociology', 'psychology', 
                'political science', 'history'
            ],
            'ced': [
                'ced', 'education', 'teaching', 'pedagogy', 'instructional', 
                'teacher'
            ],
            'chs': [
                'chs', 'health', 'nursing', 'medical', 'healthcare', 
                'public health'
            ]
        }

        # Get current context
        current_college = tracker.get_slot('active_college')
        current_topic = tracker.get_slot('active_topic')
        conversation_stage = tracker.get_slot('conversation_stage')
        
        # Determine new college from message
        new_college = None
        for college, keywords in college_keywords.items():
            if any(keyword in message for keyword in keywords):
                new_college = college
                break

        events = []
        if new_college:
            # Handle college context switching
            if current_college and new_college != current_college:
                events.extend([
                    SlotSet("last_topic", current_college),
                    SlotSet("conversation_stage", "switching"),
                    SlotSet("active_topic", None)  # Clear previous topic
                ])
            
            events.extend([
                SlotSet("active_college", new_college),
                SlotSet("active_topic", f"{new_college}_general"),
                SlotSet("conversation_stage", "inquiring" if not conversation_stage else conversation_stage)
            ])
        
        return events

class ActionHandleContextSwitch(Action):
    def name(self) -> Text:
        return "action_handle_context_switch"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        active_college = tracker.get_slot('active_college')
        last_topic = tracker.get_slot('last_topic')
        conversation_stage = tracker.get_slot('conversation_stage')
        active_topic = tracker.get_slot('active_topic')
        
        interest_categories = {
            'technical': ['programming', 'coding', 'development', 'software', 'computer', 'technical'],
            'business': ['marketing', 'business', 'management', 'enterprise', 'finance'],
            'creative': ['design', 'ui', 'ux', 'interface', 'graphics', 'multimedia'],
            'research': ['research', 'analysis', 'study', 'scientific'],
            'practical': ['hands-on', 'practical', 'implementation', 'industry']
        }
        
        detected_topic = None
        for category, keywords in interest_categories.items():
            if any(keyword in message for keyword in keywords):
                detected_topic = category
                break
        
        events = []
        
        # Set active_topic first if topic is detected
        if detected_topic:
            events.append(SlotSet("active_topic", detected_topic))
        
        if conversation_stage == "switching":
            if detected_topic:
                events.extend([
                    SlotSet("last_topic", active_topic),
                    SlotSet("conversation_stage", "inquiring")
                ])
                
                if active_college == "ccs":
                    program_suggestions = {
                        'technical': 'BSCS and BSIT programs',
                        'business': 'BSIS program',
                        'creative': 'BSCA program',
                        'research': 'BSCS program',
                        'practical': 'BSIT program'
                    }
                    
                    response = (f"I notice you're interested in {detected_topic}. "
                              f"Let me tell you about our {program_suggestions.get(detected_topic, 'programs')}")
                    dispatcher.utter_message(text=response)
            else:
                # If no topic detected, ask for clarification
                dispatcher.utter_message(text="Could you tell me more specifically what you'd like to know about?")
                events.extend([
                    SlotSet("conversation_stage", "clarifying"),
                    SlotSet("active_topic", None)
                ])
        
        return events
    
class ActionHandleFollowUp(Action):
   def name(self) -> Text:
       return "action_handle_follow_up"

   def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
       active_college = tracker.get_slot('active_college')
       active_topic = tracker.get_slot('active_topic')
       program = tracker.get_slot('program')
       
       # Enhanced follow-up mappings
       follow_up_suggestions = {
           'ccs': {
               'programs_overview': [
                   "Program admission requirements",
                   "Program duration",
                   "Career opportunities"
               ],
               'facilities_info': [
                   "Laboratory equipment",
                   "Research facilities",
                   "Study areas",
                   "Usage policies"
               ],
               'faculty_info': [
                   "Faculty specializations",
                   "Consultation hours",
                   "Research interests"
               ],
               'program_specific': {
                   'bscs': [
                       "Curriculum details",
                       "Specialization tracks",
                       "Research opportunities"
                   ],
                   'bsit': [
                       "Industry certifications",
                       "Technical skills",
                       "Internship opportunities"
                   ],
                   'bsis': [
                       "Business components",
                       "Enterprise systems",
                       "Industry partners"
                   ],
                   'bsca': [
                       "Application development",
                       "UI/UX design",
                       "Project portfolio"
                   ]
               }
           }
       }

       events = []
       response = None

       if active_college in follow_up_suggestions:
           college_suggestions = follow_up_suggestions[active_college]
           
           # Handle program-specific follow-ups
           if program and 'program_specific' in college_suggestions:
               if program.lower() in college_suggestions['program_specific']:
                   suggestions = college_suggestions['program_specific'][program.lower()]
                   response = f"For {program.upper()}, would you like to know about:\n"
                   response += "\n".join(f"{i+1}. {suggestion}" for i, suggestion in enumerate(suggestions))
           
           # Handle topic-based follow-ups
           elif active_topic in college_suggestions:
               suggestions = college_suggestions[active_topic]
               response = "Would you like to know about:\n"
               response += "\n".join(f"{i+1}. {suggestion}" for i, suggestion in enumerate(suggestions))

       if response:
           dispatcher.utter_message(text=response)
           events.append(SlotSet("conversation_stage", "following_up"))
       
       return events

class ActionTrackConversation(Action):
   def name(self) -> Text:
       return "action_track_conversation"

   def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
       # Enhanced state tracking
       current_intent = tracker.latest_message.get('intent', {}).get('name')
       active_college = tracker.get_slot('active_college')
       conversation_stage = tracker.get_slot('conversation_stage')
       active_topic = tracker.get_slot('active_topic')
       
       events = []
       
       # More detailed conversation stage tracking
       if not conversation_stage:
           events.append(SlotSet("conversation_stage", "initial"))
       elif conversation_stage == "initial":
           if active_college:
               events.append(SlotSet("conversation_stage", "inquiring"))
           elif active_topic:
               events.append(SlotSet("conversation_stage", "following_up"))
       
       # Log enhanced conversation state
       print(f"Current Intent: {current_intent}")
       print(f"Active College: {active_college}")
       print(f"Active Topic: {active_topic}")
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
       
       # Enhanced follow-up mapping with new intent structure
       follow_up_map = {
           'program_details_inquiry': [
               'program_subjects',
               'program_difficulty',
               'program_career_prospects'
           ],
           'program_inquiry_bscs': [
               'bscs_subjects',
               'bscs_difficulty',
               'ccs_career_prospects'
           ],
           'program_inquiry_bsit': [
               'bsit_subjects',
               'bsit_difficulty',
               'ccs_career_prospects'
           ],
           'program_inquiry_bsis': [
               'bsis_subjects',
               'bsis_difficulty',
               'ccs_career_prospects'
           ],
           'program_inquiry_bsca': [
               'bsca_subjects',
               'bsca_difficulty',
               'ccs_career_prospects'
           ],
           'ccs_admission_requirements': [
               'university_scholarships',
               'program_duration',
               'ccs_facilities_info'
           ],
           'ccs_facilities_info': [
               'ccs_facilities_details',
               'general_facilities_usage_policy',
               'student_work_opportunities'
           ]
       }
       
       if current_intent in follow_up_map:
           suggestions = follow_up_map[current_intent]
           response = "Would you like to know about:\n"
           if active_program:
               response = f"For {active_program}, would you like to know about:\n"
           for i, suggestion in enumerate(suggestions, 1):
               # Convert intent names to readable text
               readable_suggestion = suggestion.replace('_', ' ').title()
               response += f"{i}. {readable_suggestion}\n"
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
       
       # Enhanced program comparison logic
       mentioned_programs = [prog for prog in programs if prog in message]
       
       events = []
       if len(mentioned_programs) >= 2:
           prog1, prog2 = mentioned_programs[:2]
           comparison_topic = f"compare_{prog1}_{prog2}"
           
           events.extend([
               SlotSet("active_topic", comparison_topic),
               SlotSet("program", f"{prog1}_vs_{prog2}"),
               FollowupAction("utter_ccs_program_comparison")
           ])
           
           # Set up follow-up suggestions for after comparison
           events.append(
               SlotSet("conversation_stage", "comparing")
           )
       
       return events

class ActionTrackStudentInterest(Action):
    def name(self) -> Text:
       return "action_track_student_interest"

    def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
       message = tracker.latest_message.get('text', '').lower()
       
       # Enhanced interest categories with more specific keywords
       interest_categories = {
           'technical': [
               'programming', 'coding', 'development', 'software', 'technical',
               'systems', 'computing', 'algorithms', 'hacking', 'cybersecurity'
           ],
           'business': [
               'business', 'management', 'enterprise', 'entrepreneurship',
               'finance', 'analysis', 'consulting', 'project management'
           ],
           'creative': [
               'design', 'ui', 'ux', 'interface', 'creative', 'visual',
               'graphics', 'multimedia', 'web design', 'animation'
           ],
           'research': [
               'research', 'analysis', 'study', 'innovation', 'exploration',
               'investigation', 'scientific', 'academic', 'theory'
           ],
           'practical': [
               'hands-on', 'practical', 'implementation', 'application',
               'real-world', 'industry', 'professional', 'skills'
           ]
       }
       
       # Enhanced program suggestions based on interests
       program_suggestions = {
           'technical': {
               'primary': 'BSCS',
               'secondary': 'BSIT',
               'description': 'focuses on advanced programming and technical depth'
           },
           'business': {
               'primary': 'BSIS',
               'secondary': 'BSIT',
               'description': 'combines IT with business processes'
           },
           'creative': {
               'primary': 'BSCA',
               'secondary': 'BSIT',
               'description': 'emphasizes application development and design'
           },
           'research': {
               'primary': 'BSCS',
               'secondary': 'BSIS',
               'description': 'offers strong theoretical and research foundations'
           },
           'practical': {
               'primary': 'BSIT',
               'secondary': 'BSCA',
               'description': 'provides hands-on technical experience'
           }
       }
       
       # Track identified interests
       interests = []
       for category, keywords in interest_categories.items():
           if any(keyword in message for keyword in keywords):
               interests.append(category)
       
       events = []
       if interests:
           # Generate personalized response based on interests
           primary_suggestions = []
           for interest in interests:
               suggestion = program_suggestions[interest]
               primary_suggestions.append(
                   f"{suggestion['primary']} ({suggestion['description']})"
               )
           
           response = (
               f"Based on your interests in {', '.join(interests)}, "
               f"you might want to consider:\n"
               f"{' or '.join(set(primary_suggestions))}."
           )
           dispatcher.utter_message(text=response)
           
           # Set slots for tracking interests
           events.extend([
               SlotSet("active_topic", "program_recommendation"),
               SlotSet("conversation_stage", "recommending")
           ])
       
       return events

class ActionHandleMultipleQuestions(Action):
   def name(self) -> Text:
       return "action_handle_multiple_questions"

   def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
       message = tracker.latest_message.get('text', '').lower()
       
       # Enhanced question detection
       question_markers = {
           'what': 'information',
           'how': 'process/method',
           'where': 'location',
           'when': 'timing',
           'who': 'person/entity',
           'why': 'reason',
           'can': 'possibility',
           'does': 'verification',
           'is': 'confirmation',
           'are': 'status',
           'should': 'recommendation'
       }
       
       questions = []
       sentences = message.split('?')
       
       for sentence in sentences:
           sentence = sentence.strip()
           if any(marker in sentence for marker in question_markers):
               # Identify question type
               for marker, q_type in question_markers.items():
                   if marker in sentence:
                       questions.append({
                           'text': sentence,
                           'type': q_type,
                           'marker': marker
                       })
                       break
       
       if len(questions) > 1:
           dispatcher.utter_message(
               text="I noticed you have multiple questions. Let me address them one by one:"
           )
           
           for i, question in enumerate(questions, 1):
               response = (
                   f"{i}. Regarding your {question['type']} question: "
                   f"'{question['text']}'"
               )
               dispatcher.utter_message(text=response)
               
           # Set conversation stage for multiple questions
           return [SlotSet("conversation_stage", "answering_multiple")]
       
       return []
   
    
