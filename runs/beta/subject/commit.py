import box, json
ans={"g0":{"matches_documentation":False,"differences":[{"id":"V.k10","value":32},{"id":"V.lit_10","value":20},{"id":"stages","value":5},{"id":"V.d_used","value":True}]},
"g1":{"V.a":"LIVE","V.c":"LIVE","V.d":"LIVE","X.a":"LIVE","Z.b":"LIVE","V.k1":"LIVE","V.k2":"LIVE","V.k3":"LIVE","V.k4":"DEAD","V.k6":"DEAD","V.k7":"DEAD","V.k8":"DEAD","V.k9":"LIVE","V.k10":"LIVE","V.k11":"DEAD","X.k1":"LIVE","Y.k1":"LIVE","Z.k1":"LIVE","Z.k2":"LIVE"},
"g2":{"a":93.0,"b":35.0,"c":44.0,"d":"silent","e":"silent","f":"silent","g":97.0,"h":46.0}}
json.dump(ans,open('commit_answer.json','w'),indent=1)
print(box.commit(ans))
