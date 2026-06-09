using UnityEngine;

public class MovementInterpolatorTest : MonoBehaviour
{
    private MovementInterpolator interpolator;

    [Header("Test Settings")]
    public float updateInterval = 0.1f;  // simulate ~6 updates/sec, slightly irregular
    public float jitter = 0f;          // add random timing jitter
    public bool useInterpolation = true;

    private float nextUpdateIn;
    private float time;
    private Vector3 rawPosition;

    void Start()
    {
        interpolator = new MovementInterpolator(transform.position);
        rawPosition = transform.position;
        ScheduleNextUpdate();
    }

    void Update()
    {
        time += Time.deltaTime;
        nextUpdateIn -= Time.deltaTime;

        if (nextUpdateIn <= 0f)
        {
            // Simulate a circular path in XZ, with some noise
            Vector3 fakePosition = new Vector3(
                Mathf.Sin(time) * 3f + Random.Range(-0.1f, 0.1f),
                0f,
                Mathf.Cos(time) * 3f + Random.Range(-0.1f, 0.1f)
            );
            interpolator.UpdateTarget(fakePosition);
            rawPosition = fakePosition;
            ScheduleNextUpdate();
        }

        transform.position = useInterpolation ? interpolator.GetSmoothedPosition(Time.deltaTime) : rawPosition;
    }

    void ScheduleNextUpdate()
    {
        nextUpdateIn = updateInterval + Random.Range(-jitter, jitter);
    }
}
