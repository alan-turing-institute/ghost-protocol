using UnityEngine;

public class KeyboardCameraController : MonoBehaviour
{
    public float moveSpeed = 5f;
    public float fastMoveSpeed = 15f;
    public float lookSpeed = 2f;

    private float yaw;
    private float pitch;

    void Start()
    {
        Vector3 angles = transform.eulerAngles;
        yaw = angles.y;
        pitch = angles.x;

        // Optional: hide/lock mouse cursor while playing.
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    void Update()
    {
        float speed = Input.GetKey(KeyCode.LeftShift) ? fastMoveSpeed : moveSpeed;

        // WASD movement
        float x = Input.GetAxisRaw("Horizontal"); // A/D
        float z = Input.GetAxisRaw("Vertical");   // W/S

        Vector3 move = transform.right * x + transform.forward * z;

        // Up/down movement
        if (Input.GetKey(KeyCode.E))
            move += Vector3.up;

        if (Input.GetKey(KeyCode.Q))
            move += Vector3.down;

        transform.position += move.normalized * speed * Time.deltaTime;

        // Mouse look
        yaw += Input.GetAxis("Mouse X") * lookSpeed;
        pitch -= Input.GetAxis("Mouse Y") * lookSpeed;
        pitch = Mathf.Clamp(pitch, -89f, 89f);

        transform.rotation = Quaternion.Euler(pitch, yaw, 0f);

        // Escape unlocks the cursor
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
    }
}
