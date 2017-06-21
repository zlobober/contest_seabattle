from lxml import etree as ET
import time

cache_url = None
cache_result = None
cache_time = None

def parse_xml(url):
    global cache_url, cache_result, cache_time
    if not cache_result is None and cache_url == url and time.time() - cache_time < 3.0:
        return cache_result
    print "Cache expired, making request..."

    cache_time = time.time()
    cache_url = url

    import urllib2
    try:
        request = urllib2.urlopen(url)
        xml = request.read()
    except Exception, err:
        print "Exception while downloading xml:", str(err) 
        return None

    tree = ET.fromstring(xml) 
    problem_nodes = tree.findall("contest/challenge/problem")
    problems = [{"alias": problem.get("alias"), "title": problem.get("name")} for problem in problem_nodes]

    matrix = dict()
    session_nodes = tree.findall("contest/session")
    
    unsuccessful_submits = dict()
    names = dict()

    for session in session_nodes:
        alias = session.get("alias")
        matrix[alias] = {}
        problem_nodes = session.findall("problem")
        names[alias] = session.get("party")
        for problem in problem_nodes:
            state = "n/a"
            run_nodes = problem.findall("run")
            for run in run_nodes:
                if run.get("accepted") == "yes":
                    state = "shot"
                    break
                else:
                    state = "miss"
                    unsuccessful_submits[alias] = unsuccessful_submits.get(alias, 0) + 1
            matrix[alias][problem.get("alias")] = state 

    result = {"problems": problems, "matrix": matrix, "unsuccessful_submits": unsuccessful_submits, "names": names}
    cache_result = result
    return result
