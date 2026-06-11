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
    [Header("WebSocket")]
    public string serverUrl = "ws://localhost:8080";
 
    [Header("Translation offset (Unity units)")]
    public Vector3 positionOffset = Vector3.zero;
 
    [Header("Scale applied to incoming world position")]
    public Vector3 positionScale = Vector3.one;
 
    [Header("Rotation offset (Euler degrees)")]
    public Vector3 rotationOffset = Vector3.zero;
 
    // Read-only: the final computed camera position after transform, before smoothing
    public Vector3 TranslatedPosition { get; private set; }
 
    // ── WebSocket ────────────────────────────────────────────────────────────
    private WebSocket _ws;
    private readonly Queue<HeadLocationMessage> _messageQueue = new();
 
    // ── Smoothing ────────────────────────────────────────────────────────────
    private Vector3 _previousPosition;
    private Vector3 _targetPosition;
    private Vector3 _velocity;
    private float _measuredInterval = 0.1f;
    private float _elapsedSinceUpdate = 0f;
    private float _lastUpdateTime = 0f;
    private bool _hasTarget = false;
 
    // ── Lifecycle ────────────────────────────────────────────────────────────
 
    async void Start()
    {
        _previousPosition = transform.position;
        _targetPosition   = transform.position;
 
        _ws = new WebSocket(serverUrl);
        _ws.OnOpen    += () => Debug.Log("WS connected");
        _ws.OnError   += e  => Debug.LogError($"WS error: {e}");
        _ws.OnClose   += e  => Debug.Log($"WS closed: {e}");
        _ws.OnMessage += OnRawMessage;
 
        await _ws.Connect();
    }
 
    void Update()
    {
        // NativeWebSocket requires this on non-WebGL platforms
        #if !UNITY_WEBGL || UNITY_EDITOR
        _ws?.DispatchMessageQueue();
        #endif
 
        // Drain any queued messages, keeping only the latest
        HeadLocationMessage latest = null;
        lock (_messageQueue)
        {
            while (_messageQueue.Count > 0)
                latest = _messageQueue.Dequeue();
        }
 
        if (latest != null)
            ApplyNewTarget(latest);
 
        // Apply smoothed position every frame
        if (_hasTarget)
        {
            _elapsedSinceUpdate += Time.deltaTime;
            transform.position = GetSmoothedPosition();
        }
 
        transform.rotation = Quaternion.Euler(rotationOffset);
    }
 
    async void OnApplicationQuit()
    {
        if (_ws != null && _ws.State == WebSocketState.Open)
            await _ws.Close();
    }
 
    // ── WebSocket message handling ───────────────────────────────────────────
 
    void OnRawMessage(byte[] data)
    {
        var json = System.Text.Encoding.UTF8.GetString(data);
        try
        {
            var msg = JsonUtility.FromJson<HeadLocationMessage>(json);
            lock (_messageQueue) _messageQueue.Enqueue(msg);
            Debug.Log($"Received message {msg}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Bad message: {json}\n{e.Message}");
        }
    }
 
    // ── Transform + smoothing target ─────────────────────────────────────────
 
    void ApplyNewTarget(HeadLocationMessage msg)
    {
        float[] loc = msg.headLocation.location;
        Vector3 raw = new Vector3(loc[0], loc[1], loc[2]);
 
        // World → Unity space
        Vector3 scaled      = Vector3.Scale(raw, positionScale);
        Vector3 translated  = scaled + positionOffset;
        TranslatedPosition  = translated;
 
        // Update smoothing state
        float now = Time.time;
        _measuredInterval    = Mathf.Clamp(now - _lastUpdateTime, 0.016f, 0.5f);
        _lastUpdateTime      = now;
        _velocity            = (translated - _targetPosition) / _measuredInterval;
        _previousPosition    = _targetPosition;
        _targetPosition      = translated;
        _elapsedSinceUpdate  = 0f;
        _hasTarget           = true;
    }
 
    // ── Smoothing ────────────────────────────────────────────────────────────
 
    Vector3 GetSmoothedPosition()
    {
        if (_elapsedSinceUpdate <= _measuredInterval)
        {
            // Interpolate between last known and current target
            float t = _elapsedSinceUpdate / _measuredInterval;
            return Vector3.Lerp(_previousPosition, _targetPosition, t);
        }
        else
        {
            // No newer message arrived, so hold the last requested position.
            return _targetPosition;
        }
    }
}
