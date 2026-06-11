using UnityEngine;

public class shark_behaviour : MonoBehaviour
{
    public float speed = 2f;
    public float radiusX = 3f;
    public float radiusY = 5f;

    private Vector3 center;
    private float angle;
    private float angularSpeed;

    void Start()
    {
        // Start at top of ellipse so initial movement is in the -x direction
        center = transform.position + new Vector3(0, 0, -radiusY);
        angle = Mathf.PI / 2f;
        angularSpeed = speed / radiusX;
    }

    void Update()
    {
        angle += angularSpeed * Time.deltaTime;
        transform.position = new Vector3(
            center.x + radiusX * Mathf.Cos(angle),
            center.y,
            center.z + radiusY * Mathf.Sin(angle)
        );

        // Tangent of the ellipse gives the forward swimming direction
        Vector3 forward = new Vector3(
            -radiusX * Mathf.Sin(angle),
            0f,
            radiusY * Mathf.Cos(angle)
        );
        // Model faces local -x, so correct by 90° around Y before applying LookRotation
        if (forward != Vector3.zero)
            transform.rotation = Quaternion.LookRotation(forward) * Quaternion.Euler(0, 90, 0);
    }
}
