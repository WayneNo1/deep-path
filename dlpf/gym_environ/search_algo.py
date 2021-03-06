import collections

from scipy.spatial.distance import euclidean

from .utils import BY_PIXEL_ACTION_DIFFS


StepResult = collections.namedtuple('StepResult',
                                    'must_continue best_next new_variants_with_ratings'.split(' '))

class BaseSearchAlgo(object):
    def __init__(self):
        pass

    def reset(self, local_map, start, finish):
        self.local_map = local_map
        self.start = start
        self.finish = finish

        self.queue = [self.start]
        self.ratings = { self.start : 0 }
        self.backrefs = { self.start : self.start }
        self.visited_nodes = set()

    def walk_to_finish(self):
        while self.step().must_continue:
            pass

    def step(self):
        if self.goal_achieved():
            return StepResult(False, self.finish, [])

        while len(self.queue) > 0:
            self._reorder_queue()
            best_next = self.queue.pop()
            self.visited_nodes.add(best_next)

            if self.goal_achieved():
                return StepResult(False, self.finish, [])

            new_variants_with_ratings = self._gen_new_variants(best_next)
            if len(new_variants_with_ratings) == 0:
                continue

            self.queue.extend(p for p, _ in new_variants_with_ratings)
            self.ratings.update(new_variants_with_ratings)
            self.backrefs.update((new_point, best_next) for new_point, _ in new_variants_with_ratings)
            return StepResult(True, best_next, new_variants_with_ratings)

        return StepResult(False, None, [])

    def update_ratings(self, updates):
        self.ratings.update(updates)

    def goal_achieved(self):
        return self.finish in self.visited_nodes

    def get_best_path(self):
        self.walk_to_finish()
        if not self.goal_achieved():
            return None

        result = [self.finish]
        while result[-1] != self.start:
            result.append(self.backrefs[result[-1]])
        result.reverse()
        return result

    def _reorder_queue(self):
        self.queue.sort(key = self.ratings.__getitem__)

    def _gen_new_variants(self, pos):
        '''Proceed from the given state.
        Should return an iterable of pairs (new_state, rating).
        The bigger the rating the better the new_state is.'''
        raise NotImplemented()


class EuclideanAStar(BaseSearchAlgo):
    def _gen_new_variants(self, pos):
        y, x = pos
        all_new_points = ((y + dy, x + dx)
                          for dy, dx
                          in BY_PIXEL_ACTION_DIFFS.viewvalues())
        return [(point, -euclidean(point, self.finish))
                for point in all_new_points
                if (not point in self.backrefs)
                    and (0 <= point[0] < self.local_map.shape[0])
                    and (0 <= point[1] < self.local_map.shape[1])
                    and (self.local_map[point] == 0)]


_SEARCH_ALGOS = {
    'astar' : EuclideanAStar
}


def get_available_search_algos():
    return list(_SEARCH_ALGOS.keys())


DEFAULT_SEARCH_ALGO = 'astar'

def get_search_algo(name = DEFAULT_SEARCH_ALGO, *args, **kwargs):
    assert name in _SEARCH_ALGOS, "Unknown search algo %s" % name
    return _SEARCH_ALGOS[name](*args, **kwargs)
