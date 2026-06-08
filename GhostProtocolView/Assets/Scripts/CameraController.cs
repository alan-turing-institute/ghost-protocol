using UnityEngine;
using System;
using NativeWebSocket;
using System.Collections.Generic;

[System.Serializable]
public class CameraCommand
{
    public float x;
    public float y;
    public float z;
    public float speed;       // units/sec for move


}


public class CameraController : MonoBehaviour
{
    public string serverUrl = "ws://localhost:8080";
    public float defaultMoveSpeed = 5f;
    private WebSocket _ws;
    private readonly Queue<CameraCommand> _commandQueue = new();

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
        var json = System.Text.Encoding.UTF8.GetString(data);
        try
        {
            var cmd = JsonUtility.FromJson<CameraCommand>(json);
            Debug.Log($"Received command {cmd}");
            lock (_commandQueue) _commandQueue.Enqueue(cmd);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Bad message: {json}\n{e.Message}");
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
    }

    void ProcessCommand(CameraCommand cmd)
    {
        float moveSpeed   = cmd.speed > 0 ? cmd.speed : defaultMoveSpeed;
        var   delta       = new Vector3(cmd.x, cmd.y, cmd.z);
        
        // Moves relative to camera's current orientation
        transform.Translate(delta * moveSpeed * Time.deltaTime, Space.Self);
                
    }

    async void OnApplicationQuit()
    {
        if (_ws != null && _ws.State == WebSocketState.Open)
            await _ws.Close();
    }
}

