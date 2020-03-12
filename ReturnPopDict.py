def get_pop_dict(dic,item_key,*args):
    if len(*args) == 0:
        new_dict = {}
        if item_key in dic:
            temp = dic[item_key]
            dic.pop(item_key)
            new_dict[temp] =dic
            return new_dict
        return f"argument not in {dic}"
