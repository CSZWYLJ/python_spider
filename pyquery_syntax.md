#### 一、获取节点
1. 仅仅获取子节点：
    find(".el")
2. 获取子孙节点(包括子节点)：
    children("#el")paren
3. 获取父节点：
    parent()
    parents()  --  获取父节点或者祖先节点
4. 获取兄弟节点:
    siblings()

#### 二、获取属性和文本
1. 获取属性
--a.attr("href")
--a.attr.href

2. 获取文本
--a.text("el")

3. 获取html
--html()

4. remove()
用于提取信息，例如该信息为
```html
<a>
    外元素a的内容
    <li>
        内元素li的内容
    </li>
</a>
```
只想要a的内容时，若直接text()会获得两个内容，此时将li移去即可获得a内容
~~~
doc = pq(html)
a = doc("a")
con = a.children("li").remove()
~~~

5. 其他方法
append(),empty(),prepend()等等和jQuery用法一致
可参考:http://pyquery.readthedocs.io/en/latest/api.html

#### 三、使用注意
1. 所有的方法都可以传入参数
2. attr()方法在传入一个参数时，则是获取这个属性的值；在传入两个参数时，则是修改属性值，若标签中没有属性则新增
3. text()和html()不传参数则是获取节点内的纯文本或HTML文本，传入参数则是进行赋值
4. 当你在获取节点、属性等信息时，结果本应返回类似xpath、beautifulSoup等的列表结果，即多个结果，但是pyquery只返回第一个，此时应当采用遍历 a.items() 的方法获取多个结果