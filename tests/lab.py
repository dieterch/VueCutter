

# if inplace:
#     nexc_lst = ["self._mcut_binary","-r","-n",f"'{movie.title}'","-d", f"'{movie.summary}'",f"{self._pathname(movie)}","-c"]
# else:
#     nexc_lst = ["self._mcut_binary","-n",f"'{movie.title}'","-d", f"'{movie.summary}'",f"{self._pathname(movie)}","-c"]

# for cut in cutlist:
#     for key, value in cut.items():
#             nexc_lst.append(value)

cutlist = [{'t0': '00:00:00', 't1': '00:32:22'}, {'t0': '00:37:38', 't1': '00:55:58'}]
nexc_lst = ['a','b','c','d','e','f','g']
next_lst = nexc_lst + [v for c in cutlist for k,v in c.items()]
print(next_lst)
next_lst.insert(1,'-r')
print(next_lst)