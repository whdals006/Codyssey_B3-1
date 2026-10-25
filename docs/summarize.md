# 모듈마다 함수 요약

## doubly_linked_list.py

* class Node

    * \__init__()

* class DoublyLinkedList

    * \__init__()
    * insert_front()
    * insert_back()
    * remove_front()
    * remove_back()
    * remove_node()
    * move_to_front()
    * size()
    * \__len__
    * \__iter__

## hash_map.py

* class HashEntry

    * \__init__()

* class HashMap

    * \__init__()
    * _hash
    * _find_node()
    * put()
    * get()
    * remove()
    * contains()
    * keys()
    * size()
    * _resize()


## min_heap.py

* class MinHeap

    * \__init__()
    * push()
    * pop()
    * peek()
    * size()
    * _heapify_up()
    * _heapify_down()

## storage.py

* class StoredEntry

    * \__init__()

* class MiniRedisStore

    * \__init__()

        HashMap으로 데이터를 빠르게 찾고,
        DoublyLinkedList로 사용 순서(LRU)를 줄 세우고,
        MinHeap으로 수명이 다 된 데이터(TTL)를 골라내며,
        메모리 변수(used_memory, maxmemory)로 하드웨어 자원까지 철저히 통제한다.

    * _utf8_size()


## 저장 데이터

* HashMap : HashEntry 객체 (key, value)
* Double_linked_List : Node 객체 (prev, data, next)
* min_Heap : (expire_at, key) 튜플 형태
