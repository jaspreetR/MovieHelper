# -*- coding: utf-8 -*-
from justwatch import JustWatch

class SlotNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class MovieQueryFailureException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
        
class ProviderNotFound(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
        
def get_slot_value_from_intent(intent, slot):
    if 'slots' in intent and slot in intent['slots'] and 'value' in intent['slots'][slot]:
        slot_value = intent['slots'][slot]['value']
        return slot_value
    
    raise SlotNotFoundException('{} slot is empty'.format(slot))
        
def get_movie_name_from_intent(intent):
    return get_slot_value_from_intent(intent, 'Movie')
    
def get_provider_name_from_intent(intent):
    return get_slot_value_from_intent(intent, 'Provider')
    
def get_movie_info_from_query(query):
    if query['items'] and query['items'][0]:
        movie_info = query['items'][0]
        return movie_info
        
    raise MovieQueryFailureException('No movies found in search query')
    
def get_provider_id_from_name(provider_name):
    name = provider_name.split()[0]
    name = name.lower()
    if name == 'netflix':
        return NETFLIX_PROVIDER_ID
    elif name == 'amazon':
        return AMAZON_PROVIDER_ID
    
    raise ProviderNotFound('{} not found in provider list'.format(provider_name))
    

""" simple fact sample app """

SKILL_NAME = "Movie Helper"
LAUNCH_MESSAGE = "What films would you like to know more about?"
HELP_MESSAGE = "You can ask me a question about a film, or you can say exit ... What can I help you with?"
HELP_REPROMPT = "What can I help you with?"
STOP_MESSAGE = "Goodbye!"
FALLBACK_MESSAGE = "I cannot help with that. Movie Helper is able to answer any film-related questions you may have. What can I help you with?"
FALLBACK_REPROMPT = 'What can I help you with?'

MOVIE_DESCRIPTION_ERROR_MESSAGE = "I'm sorry I cannot find the description of this movie"
MOVIE_RELEASE_YEAR_ERROR_MESSAGE = "I'm sorry I cannot find the release year of this movie"
MOVIE_PROVIDER_ERROR_MESSAGE = "I'm sorry I cannot find the providers of this movie"
MOVIE_RUNTIME_ERROR_MESSAGE = "I'm sorry I cannot find the runtime of this movie"

NETFLIX_PROVIDER_ID = 8
AMAZON_PROVIDER_ID = 9 

just_watch = JustWatch(country='GB')

# --------------- App entry point -----------------

def lambda_handler(event, context):
    """  App entry point  """

    #print(event)

    if event['session']['new']:
        on_session_started()

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended()

# --------------- Response handlers -----------------

def on_intent(request, session):
    """ called on receipt of an Intent  """

    intent = request['intent']
    intent_name = intent['name']

    # process the intents
    if intent_name == "MovieDescriptionIntent":
        return get_movie_description_response(intent, session)
    elif intent_name == "MovieReleaseYearIntent":
        return get_movie_release_year_response(intent, session)
    elif intent_name == "MovieProviderIntent":
        return get_movie_provider_response(intent, session)
    elif intent_name == "MovieRuntimeIntent":
        return get_movie_runtime_response(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.StopIntent":
        return get_stop_response()
    elif intent_name == "AMAZON.CancelIntent":
        return get_stop_response()
    elif intent_name == "AMAZON.FallbackIntent":
        return get_fallback_response()
    else:
        print("invalid Intent reply with help")
        return get_help_response()

def get_movie_description_response(intent, session):
    
    movie_name = get_movie_name_from_intent(intent)
    results = just_watch.search_for_item(query=movie_name)
    movie_info = get_movie_info_from_query(results)
    print(movie_info)
        
    if 'short_description' in movie_info:
        speech_output = '{} has the following description: {}'.format(movie_info['title'], movie_info['short_description'])
    else:
        speech_output = MOVIE_DESCRIPTION_ERROR_MESSAGE
        
    card_content = movie_name

    return response(speech_response_with_card(SKILL_NAME, speech_output,
                                                          card_content, False))

def get_movie_release_year_response(intent, session):
    
    movie_name = get_movie_name_from_intent(intent)
    results = just_watch.search_for_item(query=movie_name)
    movie_info = get_movie_info_from_query(results)
        
    if 'original_release_year' in movie_info:
        speech_output = '{} was originally released in {}'.format(movie_info['title'], movie_info['original_release_year'])
    else:
        speech_output = MOVIE_RELEASE_YEAR_ERROR_MESSAGE
        
    card_content = movie_name

    return response(speech_response_with_card(SKILL_NAME, speech_output,
                                                          card_content, False))
                                                          
def get_movie_provider_response(intent, session):
    
    movie_name = get_movie_name_from_intent(intent)
    provider_name = get_provider_name_from_intent(intent)
    provider_id = get_provider_id_from_name(provider_name)
    results = just_watch.search_for_item(query=movie_name)
    movie_info = get_movie_info_from_query(results)
        
    speech_output = 'No, {} does not offer {}'.format(provider_name, movie_info['title'])
    if 'offers' in movie_info:
        for offer in movie_info['offers']:
            if offer['provider_id'] == provider_id:
                speech_output = 'Yes, {} is available on {}'.format(movie_info['title'], provider_name)
                break
    else:
        speech_output = MOVIE_PROVIDER_ERROR_MESSAGE
        
    card_content = movie_name

    return response(speech_response_with_card(SKILL_NAME, speech_output,
                                                          card_content, False))
                                                          
def get_movie_runtime_response(intent, session):
    
    movie_name = get_movie_name_from_intent(intent)
    results = just_watch.search_for_item(query=movie_name)
    movie_info = get_movie_info_from_query(results)
        
    if 'runtime' in movie_info:
        speech_output = '{} runs for {} minutes'.format(movie_info['title'], movie_info['runtime'])
    else:
        speech_output = MOVIE_RUNTIME_ERROR_MESSAGE
        
    card_content = movie_name

    return response(speech_response_with_card(SKILL_NAME, speech_output,
                                                          card_content, False))

def get_help_response():
    """ get and return the help string  """

    speech_message = HELP_MESSAGE
    return response(speech_response_prompt(speech_message,
                                                       speech_message, False))
def get_launch_response():
    """ get and return the help string  """

    speech_output = LAUNCH_MESSAGE
    return response(speech_response(speech_output, False))

def get_stop_response():
    """ end the session, user wants to quit the game """

    speech_output = STOP_MESSAGE
    return response(speech_response(speech_output, True))

def get_fallback_response():
    """ end the session, user wants to quit the game """

    speech_output = FALLBACK_MESSAGE
    return response(speech_response(speech_output, False))

def on_session_started():
    """" called when the session starts  """
    #print("on_session_started")

def on_session_ended():
    """ called on session ends """
    #print("on_session_ended")

def on_launch(request):
    """ called on Launch, we reply with a launch message  """

    return get_launch_response()


# --------------- Speech response handlers -----------------

def speech_response(output, endsession):
    """  create a simple json response  """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }

def dialog_response(endsession):
    """  create a simple json response with card """

    return {
        'version': '1.0',
        'response':{
            'directives': [
                {
                    'type': 'Dialog.Delegate'
                }
            ],
            'shouldEndSession': endsession
        }
    }

def speech_response_with_card(title, output, cardcontent, endsession):
    """  create a simple json response with card """

    return {
        'card': {
            'type': 'Simple',
            'title': title,
            'content': cardcontent
        },
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_and_prompt(output, endsession, reprompt_text):
    """ create a Ssml response with prompt  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def speech_response_prompt(output, reprompt_text, endsession):
    """ create a simple json response with a prompt """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': endsession
    }

def response(speech_message, session={}):
    """ create a simple json response  """
    return {
        'version': '1.0',
        'sessionAttributes' : session,
        'response': speech_message
    }