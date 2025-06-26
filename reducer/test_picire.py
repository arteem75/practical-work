import picire

def interesting(candidate):
    return len(candidate) < 3

class TestCase:
    def __init__(self, content):
        self.content = content

    def __call__(self, candidate_indices):
        candidate = [self.content[i] for i in candidate_indices]
        return picire.Outcome.FAIL if interesting(candidate) else picire.Outcome.PASS
content = [1, 2, 3, 4, 5]

dd_obj = picire.DD(
    TestCase(content),
    split=picire.splitter.BalancedSplit(n=2),  
    cache=picire.cache.NoCache(),              
    config_iterator=picire.iterator.forward      
)

full_config = list(range(len(content)))  
minimal_indices = dd_obj(full_config)

minimal_config = [content[i] for i in minimal_indices]
print("Minimal configuration:", minimal_config)
