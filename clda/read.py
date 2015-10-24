#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sys
import cPickle as pickle

'''
Parameters to set
'''
vocab_file = '../data/jstor.vocab'
corpus_file = '../data/jstor.clda'
result_file = 'jstor.pkl'
title = ['Science', 'Humanities']



id2word = dict(enumerate([x.strip() for x in open(vocab_file, 'r')]))

Y, Z, alpha, n_iter, T0, Tc, V, C, D, word2id = pickle.load(open(result_file, 'rb'))
z0 = np.zeros((T0, V), dtype=np.uint32)
z = np.zeros((T0, V, C), dtype=np.uint32)
zc = []
for i in xrange(C):
    zc.append(np.zeros((Tc[i] - T0, V), dtype=np.uint32))

n00, n01 = [0,0],[0,0]
n1 = [0,0]
with open(corpus_file, 'r') as f:
    k = 0
    for line in f:
        line = line.strip().split()
        c = int(line[0])
        dy, dz = Y[k], Z[k]
        line = line[1:]
        assert len(line) == len(dy)
        for w, y, iz, in zip(line, dy, dz):
            w = word2id[w]
            if iz < T0:
                if y == 0:
                    z0[iz, w] += 1
                else:
                    z[iz, w, c] += 1
            else:
                zc[c][iz - T0, w] += 1
        k += 1


id2id = dict([(idx, int(word)) for word, idx in word2id.items()])

N = z0.shape[1]

mapping = []
for idx in xrange(N):
    mapping.append(id2word[id2id[idx]])
mapping = np.asarray(mapping)

z0 = np.array(z0, dtype=float)
z = np.array(z, dtype=float)
for i in xrange(C):
    zc[i] = np.array(zc[i], dtype=float)

n0 = z0.sum(1)
n0c = z.sum(1)
nnc = n0c.sum(1)
nc = []
for i in xrange(C):
    nc.append(zc[i].sum(1))

z0 /= z0.sum(1)[:,np.newaxis]
t0 = z0.argsort(1)[:,::-1][:,:10]
t0c = np.zeros((T0, 10, C))
tc = []
for i in xrange(C):
    tc.append(np.zeros((Tc[i] - T0, 10)))
for c in xrange(C):
    z[:,:,c] /= z[:,:,c].sum(1)[:,np.newaxis]
    zc[c] /= zc[c].sum(1)[:,np.newaxis]
    t0c[:,:,c] = z[:,:,c].argsort(1)[:,::-1][:,:10]
    tc[c] = zc[c].argsort(1)[:,::-1][:,:10]

dist = 1.0 * n0 / nnc
order = dist.argsort()[::-1]
t0 = t0[order]
t0c = t0c[order]

print """
<style>
table { border: none; border-collapse: collapse; }
table td { border-left: 1px solid #000; }
table td:first-child { border-left: none; }
table, th { border: 1px solid black; }
th { text-align: left; }
</style>
"""

print "<h3>Common Topics</h4>"
for i, a in enumerate(zip(t0, t0c)):
    a0, a0c = a
    print "<h4>Common Topic %d</h4>" % (i+1)
    print '<table>'
    print '<tr>'
    print '\n'.join(['<th>' + x + '</th>' for x in ['Shared'] + title])
    print '</tr>'
    print '<tr>'
    for a in zip(a0, *zip(*a0c)):
        print '<tr>'
        print '\n'.join(['<td>'+mapping[x]+'</td>' for x in a])
        print '</tr>'
    print '</table>'

print "<h3>Non-common Topics</h3>"

for k, val in enumerate(zip(title, tc)):
    t, val = val
    print "<h4>%s</h4>" % (t)
    print '<table>'
    print '<tr>'
    print '\n'.join(['<th>%d</th>' % (i + 1) for i in xrange(Tc[k] - T0)])
    print '</tr>'
    for v in val.T:
        print '<tr>'
        print '\n'.join(['<td>%s</td>' % (mapping[i]) for i in v])
        print '</tr>'
    print '</table>'
