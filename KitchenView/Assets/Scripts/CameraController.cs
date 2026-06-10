using UnityEngine;
using System;
using NativeWebSocket;
using System.Collections.Generic;

[System.Serializable]
public class HeadLocationMessage
{
    public HeadLocation headLocation;
}

[System.Serializable]
public class HeadLocation
{
    public float[] location;
    public long timestamp;
}

public class CameraController : MonoBehaviour
{
    public string serverUrl = "ws://localhost:8080";
    public float defaultMoveSpeed = 5f;
    private WebSocket _ws;
    private readonly Queue<HeadLocationMessage> _commandQueue = new();

    [Header("Translation offset (Unity units)")]
    public Vector3 positionOffset = Vector3.zero;
 
    [Header("Scale applied to incoming world position")]
    public Vector3 positionScale = Vector3.one;
 
    [Header("Rotation offset (Euler degrees)")]
    public Vector3 rotationOffset = Vector3.zero;
 
    // The raw head position in world space, set externally
    // (e.g. by your WebSocket/UDP receiver script)
    [HideInInspector]
    public Vector3 rawHeadPosition = Vector3.zero;
 
    // Read-only: the final computed camera position after transform
    public Vector3 ComputedPosition { get; private set; }

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    async void Start()
    {
        _ws = new WebSocket(serverUrl);

        _ws.OnOpen    += () => Debug.Log("WS connected");
        _ws.OnError   += e  => Debug.LogError($"WS error: {e}");
        _ws.OnClose   += e  => Debug.Log($"WS closed: {e}");
        _ws.OnMessage += OnMessage;

        await _ws.Connect();
    }

void OnMessage(byte[] data)
    {
        var jsonString = System.Text.Encoding.UTF8.GetString(data);
        try
        {
            var msg = JsonUtility.FromJson<HeadLocationMessage>(jsonString);

            Debug.Log($"Received position {msg}");
            lock (_commandQueue) _commandQueue.Enqueue(msg);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Bad message: {jsonString}\n{e.Message}");
        }
    }

    // Update is called once per frame
    void Update()
    {

        lock (_commandQueue)
        {
            while (_commandQueue.Count > 0)
                ProcessCommand(_commandQueue.Dequeue());
        }

        // Apply scale then offset to the incoming head position
        Vector3 scaled = Vector3.Scale(rawHeadPosition, positionScale);
        Vector3 translated = scaled + positionOffset;
 
        ComputedPosition = translated;
        //transform.position = translated;
 
        // Apply rotation offset on top of any base rotation
       // transform.rotation = Quaternion.Euler(rotationOffset);
    }

    void ProcessCommand(HeadLocationMessage msg)
    {
        Vector3 rawHeadPosition = new Vector3(msg.headLocation.location[0],
                                  msg.headLocation.location[1],
                                  msg.headLocation.location[2]);
        // Apply scale then offset to the incoming head position
        Vector3 scaled = Vector3.Scale(rawHeadPosition, positionScale);
        Vector3 translated = scaled + positionOffset;
 
        ComputedPosition = translated;
        transform.position = translated;
 
        // Apply rotation offset on top of any base rotation
        transform.rotation = Quaternion.Euler(rotationOffset);
                
    }

    async void OnApplicationQuit()
    {
        if (_ws != null && _ws.State == WebSocketState.Open)
            await _ws.Close();
    }
}

