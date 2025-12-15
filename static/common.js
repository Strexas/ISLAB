//Call the delete reservation api function
async function delete_reservation(id)
{
  const res = await fetch(`/reservations/delete/${id}`, {
    method: "DELETE",
    headers: { "Accept": "application/json" }
  });

  const data = await res.json();
  
  if (res.ok)
    location.reload();
  else
    alert(data.error || "Failed to delete");
}