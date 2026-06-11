using UnityEngine;

public class KeyboardCameraController : MonoBehaviour
{
    public float moveSpeed = 2f;
    public float fastMoveSpeed = 15f;

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
    }
}
