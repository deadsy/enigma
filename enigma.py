#!/usr/bin/python

#------------------------------------------------------------------------------

def norm(s):
  # lower case
  s = s.lower()
  x = []
  for c in s:
    i = ord(c) - ord('a')
    # only a-z
    if i >= 0 and i <= 25:
      x.append(i)
  return tuple(x)

def denorm(x):
  return ''.join([chr(c + ord('a')) for c in x])

#------------------------------------------------------------------------------

def gen_reverse(x):
  r = [0,] * len(x)
  for i in range(len(x)):
    r[x[i]] = i
  return r

#------------------------------------------------------------------------------

class rotor(object):

  def __init__(self, r):
    ((t, turnover), ofs) = r
    self.ft = norm(t)
    self.rt = gen_reverse(self.ft)
    self.turnover = norm(turnover)[0]
    self.reset_posn = norm(ofs)[0]
    self.mod = len(self.ft)
    self.reset()

  def fwd(self, c):
    c = (c + self.posn) % self.mod
    c = self.ft[c]
    c = (c - self.posn) % self.mod
    return c

  def rev(self, c):
    c = (c + self.posn) % self.mod
    c = self.rt[c]
    c = (c - self.posn) % self.mod
    return c

  def reset(self):
    self.posn = self.reset_posn

  def advance(self, carry_in):
    if not carry_in:
      return False
    carry_out = self.posn == self.turnover
    self.posn = (self.posn + 1) % self.mod
    return carry_out

  def __str__(self):
    s = []
    s.append('%s' % denorm(self.ft))
    s.append('%s' % denorm((self.turnover,)))
    s.append('%s' % denorm((self.posn,)))
    return ' '.join(s)

#------------------------------------------------------------------------------

class reflector(object):

  def __init__(self, t):
    self.t = norm(t)

  def reflect(self, c):
    return self.t[c]

  def __str__(self):
    return denorm(self.t)

#------------------------------------------------------------------------------

class plugboard(object):

  def __init__(self, t):
    self.ft = norm(t)
    self.rt = gen_reverse(self.ft)

  def fwd(self, c):
    return self.ft[c]

  def rev(self, c):
    return self.rt[c]

  def __str__(self):
    return denorm(self.ft)

#------------------------------------------------------------------------------

class enigma(object):
  def __init__(self, cfg):
    self.pb = plugboard(cfg['pb'])
    self.r0 = rotor(cfg['r0'])
    self.r1 = rotor(cfg['r1'])
    self.r2 = rotor(cfg['r2'])
    self.rf = reflector(cfg['rf'])

  def reset(self):
    self.r0.reset()
    self.r1.reset()
    self.r2.reset()

  def advance(self):
    x = self.r0.advance(True)
    x = self.r1.advance(x)
    self.r2.advance(x)

  def encrypt(self, pt):
    ct = []
    for c in pt:
      self.advance()
      c = self.pb.fwd(c)
      c = self.r0.fwd(c)
      c = self.r1.fwd(c)
      c = self.r2.fwd(c)
      c = self.rf.reflect(c)
      c = self.r2.rev(c)
      c = self.r1.rev(c)
      c = self.r0.rev(c)
      c = self.pb.rev(c)
      ct.append(c)
    return ct

  def __str__(self):
    s = []
    s.append('pb %s' % str(self.pb))
    s.append('r0 %s' % str(self.r0))
    s.append('r1 %s' % str(self.r1))
    s.append('r2 %s' % str(self.r2))
    s.append('rf %s' % str(self.rf))
    return '\n'.join(s)

#------------------------------------------------------------------------------

# reflectors
_ref_a = 'ejmzalyxvbwfcrquontspikhgd'
_ref_b = 'yruhqsldpxngokmiebfzcwvjat'
_ref_c = 'fvpjiaoyedrzxwgctkuqsbnmhl'

# rotors
_rotor_1 = ('ekmflgdqvzntowyhxuspaibrcj', 'q')
_rotor_2 = ('ajdksiruxblhwtmcqgznpyfvoe', 'e')
_rotor_3 = ('bdfhjlcprtxvznyeiwgakmusqo', 'v')
_rotor_4 = ('esovpzjayquirhxlnftgkdcmwb', 'j')
_rotor_5 = ('vzbrgityupsdnhlxawmjqofeck', 'z')

#------------------------------------------------------------------------------

_test_vectors = (
  ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bdzgowcxltksbtmcdlpbmuqofxyhcx'),
  ('doyouknowthewaytosanjose', 'miwmlorqeaxtdtcwznpzzdlz'),
)

#------------------------------------------------------------------------------
# machine setups

_em1_cfg = {
  'pb': 'abcdefghijklmnopqrstuvwxyz',
  'r0': (_rotor_3, 'a'),
  'r1': (_rotor_2, 'a'),
  'r2': (_rotor_1, 'a'),
  'rf': _ref_b,
}

#------------------------------------------------------------------------------

def main():
  em = enigma(_em1_cfg)
  print(em)

  for (pt, ct) in _test_vectors:
    em.reset()
    result = denorm(em.encrypt(norm(pt)))
    print('%s: %s' % (result, ('pass', 'fail')[result != ct]))

main()

#------------------------------------------------------------------------------
