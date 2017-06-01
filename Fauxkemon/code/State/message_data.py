fauxkemon_standard_messages={
    'cant_use_that':"Professor Oak: Now is not the time to use that...",
    'used_attack':"{} used {}!",
    'used_item':"{} used {}!",
    'super_effective':"It's super effective!",
    'no_effect':"It had no effect...",
    'doesnt_effect':"It doesn't affect {}",
    'not_very_effective':"It's not very effective",
    'missed':'The attack missed!'
    }

def get_message(m_key):
    return fauxkemon_standard_messages[m_key]
