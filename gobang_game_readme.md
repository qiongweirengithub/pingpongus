# game actions data pattern


## login
```
{
    'action':'login',
}

```

## create_room
```
{
    'action':'create_room',
    'player_id':'player_id',  
    'room_secret':'secret',
    'room_name':'room_name'
}

```


## join_room
```
{
    'action':'join_room',
    'room_id':'room_id', 
    'room_name':'room_name',
    'player_id':'player_id' ,
    'room_secret':'secret'
}

```


## exit_room
```
{
    'action':'exit_room',
    'room_id':'room_id', 
    'player_id':'player_id' 
}

```



## make_move
```
{
    'action':'make_move',
    'room_id':'room_id', 
    'player_id':'player_id',
    'poxi':'10',
    'poyi':'3',
}

```

## sync_frame   ->    schedule output to websocket
```
{
    'action':'sync_frame_success',
    [   
        {
            'room_id':'room_id', 
            'player_id':'player_id',
            'poxi':'10',
            'poyi':'3'
        },
        {    
            'room_id':'room_id', 
            'player_id':'player_id',
            'poxi':'10',
            'poyi':'3'
        }
    ]
}

```
