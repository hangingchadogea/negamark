import logging
#logging.basicConfig(level=logging.DEBUG)

from negamark import AbstractGameStateCache, Outcome
from storm.locals import *

class StormMySQLGameStateCache(AbstractGameStateCache):

  def __init__(self, database_url):
    database = create_database(database_url)
    self.store = Store(database)
    self.store.execute('CREATE TABLE IF NOT EXISTS cached_state (state BIGINT '
                       'UNSIGNED PRIMARY KEY, value INTEGER, depth INTEGER, '
                       'heuristic INTEGER)')

  def get_outcome(self, state):
    cached_state = self.store.get(CachedState, state)
    if cached_state:
      return Outcome(cached_state.value, cached_state.depth,
                     cached_state.heuristic)
    else:
      return None

  def save_outcome(self, state, value, depth, heuristic=0):
    cached_state = self.store.get(CachedState, state)
    if cached_state:
      cached_state.value=value
      cached_state.depth=depth
      cached_state.heuristic=heuristic
    else:
      cached_state = CachedState(state, value, depth, heuristic)
      self.store.add(cached_state)

  def delete_outcome(self, state):
    cached_state = self.store.get(CachedState, state)
    if cached_state:
      self.store.remove(cached_state)

  def flush(self):
    self.store.commit()
    self.store.flush()

class CachedState(object):
  __storm_table__ = 'cached_state'
  state = Int(primary=True)
  value = Int()
  depth = Int()
  heuristic = Int()

  def __init__(self, state, value, depth, heuristic=None):
    self.state = state
    self.value = value
    self.depth = depth
    self.heuristic = heuristic