using UnityEngine;

public class MovementInterpolator
{
    private Vector3 previousPosition;
    private Vector3 targetPosition;
    private Vector3 velocity; // units per second, estimated from last update delta
    private float measuredInterval = 0.1f; // updated on each real update
    private float elapsedTime = 0f;
    private float lastUpdateTime = 0f;

    public MovementInterpolator(Vector3 startPosition)
    {
        previousPosition = startPosition;
        targetPosition = startPosition;
        velocity = Vector3.zero;
    }

    public void UpdateTarget(Vector3 newPosition)
    {
        float now = Time.time;
        measuredInterval = Mathf.Max(now - lastUpdateTime, 0.016f); // guard divide-by-zero
        lastUpdateTime = now;

        // Estimate velocity from how far the target moved over the actual interval
        velocity = (newPosition - targetPosition) / measuredInterval;

        previousPosition = targetPosition;
        targetPosition = newPosition;
        elapsedTime = 0f;
    }

    public Vector3 GetSmoothedPosition(float deltaTime)
    {
        elapsedTime += deltaTime;

        if (elapsedTime <= measuredInterval)
        {
            // Within expected window: interpolate between previous and target
            float t = elapsedTime / measuredInterval;
            return Vector3.Lerp(previousPosition, targetPosition, t);
        }
        else
        {
            // Update is late: extrapolate beyond target using last known velocity
            float overtime = elapsedTime - measuredInterval;
            return targetPosition + velocity * overtime;
        }
    }
}